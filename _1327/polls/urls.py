from django.conf.urls import patterns, url


urlpatterns = patterns('_1327.polls.views',
	url(r"^$", "list", name="list"),
	url(r"(?P<poll_id>\d+)/results/$", "results", name="results"),
	url(r"(?P<poll_id>\d+)/vote/$", "vote", name="vote"),
)
