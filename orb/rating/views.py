from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from orb.models import ResourceRating


class RatingForm(forms.ModelForm):

    rating = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        fields = '__all__'
        model = ResourceRating

    def save(self, commit=True):
        if not getattr(self.instance, 'pk'):
            try:
                self.instance = ResourceRating.objects.get(**self.cleaned_data)
            except ResourceRating.DoesNotExist:
                pass
        print(self.instance)
        super(RatingForm, self).save(commit=commit)


@login_required
@require_POST
def resource_rate_view(request):

    form_data = request.POST.copy()
    form_data.update({"user": request.user.pk})
    form = RatingForm(data=form_data)

    if not form.is_valid():
        return HttpResponseBadRequest()

    form.save()
    resource = form.cleaned_data['resource']

    return JsonResponse({
        'no_ratings': ResourceRating.objects.filter(resource=resource).count(),
        'ratings_required': settings.ORB_RESOURCE_MIN_RATINGS,
    })
