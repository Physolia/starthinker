###########################################################################
#
#  Copyright 2017 Google Inc.
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

from util.project import project 
from util.data import get_emails, put_files
from util.csv import csv_to_rows, rows_to_csv, rows_date_sanitize, rows_percent_sanitize, rows_print, rows_to_type


def moat_filter(rows):
  for row in rows:
    row = row[:10]
    if '${CAMPAIGN_ID}' in row: continue
    yield row


def moat():

  # find emails with reports
  for email in get_emails(project.task['auth'], project.task['in'], project.date):
    if project.verbose: print 'PROCESSING:', email['subject']
    if len(email['attachments']) == 0: continue

    # use only first attachment
    attachment = email['attachments'][0]
    rows = csv_to_rows(attachment[1])
    rows = rows_date_sanitize(rows)
    rows = rows_percent_sanitize(rows)
    rows = rows_to_type(rows)
    rows = moat_filter(rows)

    rows = rows_print(rows, 0, 1)

    print 'MOAT Filename:', attachment[0]
    put_files(project.task['auth'], project.task['out'], attachment[0], rows_to_csv(rows))

if __name__ == "__main__":
  project.load('moat')
  moat()
