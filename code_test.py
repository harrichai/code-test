import argparse
from apiclient.discovery import build
from oauth2client .service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import files
from oauth2client import tools

def get_service(api_name, api_version, scope, key_file_location):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account JSON key file.

  Returns:
    A service that is connected to the specified API.
  """

  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      key_file_location, scopes=scopes)

  # Build the service object.
  service = build(api_name, api_version, credentials=credentials)

  return service


def get_first_profile_id(service):
  # Use the Analytics service object to get the first profile id.

  # Get a list of all Google Analytics accounts for this user
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    # Get the first Google Analytics account.
    account = accounts.get('items')[0].get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(
        accountId=account).execute()

    if properties.get('items'):
      # Get the first property id.
      property = properties.get('items')[0].get('id')

      # Get a list of all views (profiles) for the first property.
      profiles = service.management().profiles().list(
          accountId=account,
          webPropertyId=property).execute()

      if profiles.get('items'):
        # return the first view (profile) id.
        return profiles.get('items')[0].get('id')

  return None

def get_results(service, profile_id):
  # Use the Analytics Service Object to query the Core Reporting API
  # for the number of sessions within the past seven days.
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date='7daysAgo',
      end_date='today',
      metrics='ga:sessions').execute()


def print_results(results):
  # Print data nicely for the user.
  if results:
    print 'View (Profile): %s' % results.get('profileInfo').get('profileName')
    print 'Total Sessions: %s' % results.get('rows')[0][0]

  else:
    print 'No results found'


def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']
  key_file_location = '<REPLACE_WITH_JSON_FILE>'

  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, key_file_location,
    service_account_email)
  profile = get_first_profile_id(service)
  print_results(get_results(service, profile))


if __name__ == '__main__':
  main()


  #run the sample -python HelloAnalytics.py
  pip show six | grep "Location:" | cut -d " " -f2

#  There are performance gains and quota incentives when batching permission API write (delete, insert, update) requests.

#for API permissions

import json
from apiclient.errors import HttpError
from apiclient.http import BatchHttpRequest

def call_back(request_id, response, exception):
  """Handle batched request responses."""
  print request_id
  if exception is not None:
    if isinstance(exception, HttpError):
      message = json.loads(exception.content)['error']['message']
      print ('Request %s returned API error : %s : %s ' %
             (request_id, exception.resp.status, message))
  else:
    print response


def add_users(users, permissions):
  """Adds users to every view (profile) with the given permissions.

  Args:
    users: A list of user email addresses.
    permissions: A list of user permissions.
  Note: this code assumes you have MANAGE_USERS level permissions
  to each profile and an authorized Google Analytics service object.
  """

  # Get the a full set of account summaries.
  account_summaries = analytics.management().accountSummaries().list().execute()

  # Loop through each account.
  for account in account_summaries.get('items', []):
    account_id = account.get('id')

    # Loop through each user.
    for user in users:
      # Create the BatchHttpRequest object.
      batch = BatchHttpRequest(callback=call_back)

      # Loop through each property.
      for property_summary in account.get('webProperties', []):
        property_id = property_summary.get('id')

        # Loop through each view (profile).
        for view in property_summary.get('profiles', []):
          view_id = view.get('id')

          # Construct the Profile User Link.
          link = analytics.management().profileUserLinks().insert(
              accountId=account_id,
              webPropertyId=property_id,
              profileId=view_id,
              body={
                  'permissions': {
                      'local': permissions
                  },
                  'userRef': {
                      'email': user
                  }
              }
          )
          batch.add(link)

      # Execute the batch request for each user.
      batch.execute()

if __name__ == '__main__':

  # Construct a list of users.
  emails = ['ona@gmail.com', 'emi@gmail.com', 'sue@gmail.com', 'liz@gmail.com']

  # call the add_users function with the list of desired permissions.
  add_users(emails, ['READ_AND_ANALYZE'])
