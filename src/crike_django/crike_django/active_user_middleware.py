import datetime
from django.core.cache import cache
from django.conf import settings
from crike_django.views import get_profile

class ActiveUserMiddleware:
    '''
    cache all user visit time.
    when an user is online for 30 minutes, give 5 points
    '''
    hour = 60 * 60

    def process_request(self, request):
        if request.user is None:
            return

        current_user = request.user
        now = datetime.datetime.now()
        if cache.get('seen_%s' % (current_user.username)):
            start_seen = cache.get('start_seen_%s' % (current_user.username))
            if start_seen:
                delta = now - start_seen
                if delta > datetime.timedelta(minutes=30):
                    p = get_profile(current_user)
                    p.point_add(5)
                    p.save()
                    # Refresh start_seen time after points given.
                    cache.set('start_seen_%s' % (current_user.username), now,
                              self.hour)
            else:
                cache.set('start_seen_%s' % (current_user.username), now,
                          self.hour)
        else:
            cache.delete('start_seen_%s' % (current_user.username))
        cache.set('seen_%s' % (current_user.username), now,
                  settings.USER_LASTSEEN_TIMEOUT)
