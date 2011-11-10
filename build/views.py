import csv

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import CheckboxSelectMultiple
from django.db import connection
from django.http import HttpResponse

from middleware.restrict_to_remote import allow_build
import models

from django.template.defaulttags import URLNode
from django.conf import settings
from jinja2.filters import contextfilter
from django.utils import translation
from libs.jinja import jinja_render_to_response
import commonware.log

log = commonware.log.getLogger('inventory')

def build_attribute_form_generator(show_fields):
    class f(forms.ModelForm):
        purposes = forms.ModelMultipleChoiceField(queryset=models.BuildPurpose.objects.all(), 
                          widget=CheckboxSelectMultiple, required=False)
        
        class Meta:
            model = models.BuildAttribute
            fields = show_fields
            
    return f
    
class BuildAttributeForm(forms.ModelForm):
    
    purposes = forms.ModelMultipleChoiceField(queryset=models.BuildPurpose.objects.all(), 
                    widget=CheckboxSelectMultiple, required=False)
    
    class Meta:
        model = models.BuildAttribute
        fields = ('support_tier',
                  'product_series',
                  'tboxtree_url',
                  'cvsbranch',
                  'cpu_throttled',
                  'product_branch',
                  'pool_name',
                  'purposes',
                  'closes_tree',
                  'support_doc')

class BuildSystemForm(forms.ModelForm):
    
    class Meta:
        model = models.System
        fields = ('operating_system', 'ram', 'notes')

@allow_build
def quicksearch_ajax(request):
    systems = models.System.build_objects.select_related().filter(
        hostname__icontains=request.POST['quicksearch']
    ).order_by('hostname')
    return jinja_render_to_response('build/quicksearch.html', {
            'systems': systems,
           })

@allow_build
def build_show(request, id):
    system = get_object_or_404(models.System, pk=id, allocation__name='release')

    return jinja_render_to_response('build/show.html', {
            'system': system,
           })

@allow_build
def build_edit(request, id):
    system = get_object_or_404(models.System, pk=id, allocation__name='release')
    try:
        build_attribute = system.buildattribute
    except models.BuildAttribute.DoesNotExist:
        build_attribute = None

    if request.method == 'POST':
        form = BuildAttributeForm(request.POST, instance=build_attribute)
        system_form = BuildSystemForm(request.POST, instance=system)
        
        if form.is_valid() and system_form.is_valid():
            system_form.save()
            ba = form.save(commit=False)
            ba.system = system 
            ba.save()
            form.save_m2m()
            return redirect(build_list)
    else:
        form = BuildAttributeForm(instance=build_attribute) 
        system_form = BuildSystemForm(instance=system)

    return jinja_render_to_response('build/edit.html', {
            'systems': system,
            'system_form': system_form,
            'form': form,
           })

@allow_build
def build_bulk(request):
    systems = models.System.build_objects.filter(id__in=request.GET.getlist('system_id'))
    if request.method == 'POST':
        save_fields = [f for f in request.POST.getlist('save_field')
                            if f in BuildAttributeForm.Meta.fields]
        if build_attribute_form_generator(save_fields)(request.POST).is_valid():
            for s in systems:
                try:
                    build_attribute = s.buildattribute
                except models.BuildAttribute.DoesNotExist:
                    build_attribute = None
                form = build_attribute_form_generator(save_fields)(request.POST, instance=build_attribute)
                ba = form.save(commit=False)
                ba.system = s
                ba.save()
                form.save_m2m()
            return redirect(build_list)
        else:
            form = BuildAttributeForm(request.POST)
    else:
        form = BuildAttributeForm() 
    return jinja_render_to_response('build/bulk.html', {
            'systems': systems,
            'form': form,
           })

@allow_build
def build_list(request):
    systems = models.System.objects.filter(allocation__name='release').select_related().order_by('hostname')
    for s in systems:
        try:
            build_attribute = s.buildattribute
        except:
            tmp = models.BuildAttribute(id=999999999,system=s)
            s.buildattribute = tmp
    return jinja_render_to_response('build/index.html', {
            'systems': systems,
           })

@allow_build
def build_csv(request):
    systems = models.System.build_objects.all().order_by('hostname')
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=build_systems.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Host Name', 'Support Tier', 'Repo. Branch', 
                     'CPU Throttled', 'Product Branch', 'Product Series',
                     'Closes Tree', 'Purposes', 'Support URL'])
    
    for s in systems:
        try:
            row = [s.hostname, 
                   s.buildattribute.support_tier, 
                   s.buildattribute.cvsbranch, 
                   s.buildattribute.cpu_throttled, 
                   s.buildattribute.product_branch, 
                   s.buildattribute.product_series, 
                   s.buildattribute.closes_tree, 
                   ",".join(str(p) for p in s.buildattribute.purposes.all()), 
                   s.buildattribute.support_doc]
        except models.BuildAttribute.DoesNotExist:
            row = [s.hostname] + ["" for i in range(8)]
        writer.writerow(row)
        
    return response