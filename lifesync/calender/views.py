from django.shortcuts import render
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import calendar
from django.utils.timezone import make_aware
from django.utils import timezone
from configparser import ConfigParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")


def get_calander_home(request):
    """
    Renders the calendar page with Google Calendar events for the logged-in user.

    Args:
    request (HttpRequest): The request object.

    Returns:
    HttpResponse: Rendered calendar page with event data or error message.
    """

    # Get the current month and year for display purposes.
    now = timezone.now()
    current_month = now.strftime("%B")
    current_year = now.year
    tokens = request.session.get('google_oauth_tokens')
    print("TOKENS::")
    print(tokens)
    client_id = CONFIG.get("GOOGLE", "client_id")
    secret = CONFIG.get("GOOGLE", "secret")
    service = None

    # Retrieve Google OAuth tokens from the session.
    if tokens:
        try:
            creds = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=secret,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error creating Google Calendar service: {e}")
            # Optionally, redirect to a login or error page

    # Inside get_calander_home, just after retrieving tokens
    print("Tokens retrieved from session:", tokens)

    if service:
        now = timezone.now()
        start_of_month = datetime.datetime(now.year, now.month, 1).isoformat() + 'Z'
        end_of_month = datetime.datetime(now.year, now.month,
                                         calendar.monthrange(now.year, now.month)[1]).isoformat() + 'Z'

        events_result = service.events().list(calendarId='primary', timeMin=start_of_month, timeMax=end_of_month,
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        total_meetings, total_duration, event_dates = len(events), 0, set()
        online_meetings_count = 0

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_date = start[:10]  # Extract the date part
            event_dates.add(event_date)

            if start and end:  # Check if start and end times are available
                fmt = '%Y-%m-%dT%H:%M:%S%z'
                start_dt = datetime.datetime.strptime(start, fmt)
                end_dt = datetime.datetime.strptime(end, fmt)
                total_duration += (end_dt - start_dt).total_seconds()

            if 'location' in event and 'http' in event['location'].lower():
                online_meetings_count += 1

        # Create a list of all days in the current month for calendar display.
        average_duration = (total_duration / total_meetings) / 60 if total_meetings else 0
        month_days = [datetime.date(now.year, now.month, day) for day in
                      range(1, calendar.monthrange(now.year, now.month)[1] + 1)]

        upcoming_meeting = None
        now = make_aware(datetime.datetime.now())

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_dt = datetime.datetime.fromisoformat(start)

            # Find the next upcoming meeting.
            if now < start_dt:
                if upcoming_meeting is None or start_dt < upcoming_meeting['start']:
                    upcoming_meeting = {
                        'start': start_dt,
                        'title': event.get('summary', 'No Title')
                    }
        first_day_of_month = datetime.date(now.year, now.month, 1)
        first_weekday_of_month = first_day_of_month.weekday()  # Monday is 0 and Sunday is 6
        weekdays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        # context['weekdays'] = weekdays[first_weekday_of_month:] + weekdays[:first_weekday_of_month]

        event_titles_by_date = {}

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_date = start[:10]  # Extract the date part
            event_title = event.get('summary', 'No Title')
            event_dates.add(event_date)

            # Add event title to the dictionary
            if event_date in event_titles_by_date:
                event_titles_by_date[event_date].append(event_title)
            else:
                event_titles_by_date[event_date] = [event_title]

        # Create a context dictionary to pass data to the template.
        context = {
            'total_meetings': total_meetings,
            'average_duration': average_duration,
            'online_meetings_count': online_meetings_count,
            'meeting_days': sorted(list(event_dates)),
            'month_days': month_days,
            'upcoming_meeting': upcoming_meeting,
            'current_month': current_month,
            'current_year': current_year,
            'first_weekday_of_month': first_weekday_of_month,
            'weekdays': weekdays[first_weekday_of_month:] + weekdays[:first_weekday_of_month],
            'event_titles_by_date': event_titles_by_date,
        }

    else:
        context = {
            'error': 'Google Calendar service is not available.'
        }
    print(context)

    return render(request, 'calender/home.html', context)
