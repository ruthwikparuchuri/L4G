from datetime import timedelta
from django.utils.timezone import now
from main.models import Event  

def update_event_status():

    help = "Update event statuses based on current datetime"
    
    current_time = now()

    # Update Scheduled → Ongoing (1 hour before to 30 minutes after event time)
    scheduled_to_ongoing = Event.objects.filter(
        event_status="Scheduled",
        datetime__gte=current_time - timedelta(hours=1),  # 1 hour before
        datetime__lte=current_time + timedelta(minutes=30),  # 30 minutes after
    )
    scheduled_to_ongoing.update(event_status="Ongoing")

    # Update Ongoing → Completed (after 3 hours have passed)
    ongoing_to_completed = Event.objects.filter(
        event_status="Ongoing",
        datetime__lt=current_time - timedelta(hours=3)  # After 3 hours
    )
    ongoing_to_completed.update(event_status="Completed")

    print(f"Updated {scheduled_to_ongoing.count()} events to 'Ongoing'")
    print(f"Updated {ongoing_to_completed.count()} events to 'Completed'")

