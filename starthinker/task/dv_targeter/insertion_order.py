###########################################################################
#
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################


from starthinker.util import has_values
from starthinker.util.bigquery import table_create
from starthinker.util.data import get_rows
from starthinker.util.data import put_rows
from starthinker.util.google_api import API_DV360
from starthinker.util.google_api.discovery_to_bigquery import Discovery_To_BigQuery
from starthinker.util.project import project
from starthinker.util.regexp import lookup_id


def insertion_order_clear():
  table_create(
    project.task["auth_bigquery"],
    project.id,
    project.task["dataset"],
    "DV_InsertionOrders",
    Discovery_To_BigQuery(
      "displayvideo",
      "v1"
    ).method_schema(
      "advertisers.insertionOrders.list"
    )
  )


def insertion_order_load():

  # load multiple from user defined sheet
  def insertion_order_load_multiple():
    for row in get_rows(
      project.task["auth_sheets"],
      { "sheets": {
        "sheet": project.task["sheet"],
        "tab": "Advertisers",
        "range": "A2:A"
      }}
    ):
      if row:
        yield from API_DV360(
          project.task["auth_dv"],
          iterate=True
        ).advertisers().insertionOrders().list(
          advertiserId=lookup_id(row[0])
        ).execute()

  # only load if filters are missing
  if not has_values(get_rows(
    project.task['auth_sheets'],
    { 'sheets': {
      'sheet': project.task['sheet'],
      'tab': 'Line Items',
      'range': 'A2:A'
    }}
  )):

    insertion_order_clear()

    # write insertion orders to database
    put_rows(
      project.task["auth_bigquery"],
      { "bigquery": {
        "dataset": project.task["dataset"],
        "table": "DV_InsertionOrders",
        "schema": Discovery_To_BigQuery(
          "displayvideo",
          "v1"
        ).method_schema("advertisers.insertionOrders.list"),
        "format": "JSON"
      }},
      insertion_order_load_multiple()
    )
