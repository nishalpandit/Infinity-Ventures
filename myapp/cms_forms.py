from django import forms
from .models import (
    SiteBranding,
    HeroSection,
    QuickServiceCard,
    FeaturedProjectCard,
    PackageCard,
    Testimonial,
    TrustMetric,
)

class StyledModelForm(forms.ModelForm):
    """Base form applying consistent Superadmin design system styles to all inputs."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control-file'})
            else:
                existing_class = field.widget.attrs.get('class', '')
                field.widget.attrs.update({'class': f'form-control {existing_class}'.strip()})


class SiteBrandingForm(StyledModelForm):
    class Meta:
        model = SiteBranding
        fields = [
            'site_title', 'tagline', 'logo', 'favicon',
            'contact_email', 'support_phone', 'address',
            'facebook_url', 'instagram_url', 'linkedin_url', 'twitter_url', 'youtube_url',
            'copyright_text'
        ]
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'City, State, Country'}),
        }


class HeroSectionForm(StyledModelForm):
    class Meta:
        model = HeroSection
        fields = [
            'badge_text', 'headline', 'subtext', 'hero_image',
            'cta_primary_text', 'cta_primary_url',
            'cta_secondary_text', 'cta_secondary_url',
            'stat1_number', 'stat1_label',
            'stat2_number', 'stat2_label',
            'stat3_number', 'stat3_label',
        ]
        widgets = {
            'subtext': forms.Textarea(attrs={'rows': 3}),
        }


class QuickServiceCardForm(StyledModelForm):
    class Meta:
        model = QuickServiceCard
        fields = [
            'title', 'subtitle', 'image', 'price', 'discount_price',
            'duration', 'category_tag', 'badge_text', 'order', 'is_active'
        ]


class FeaturedProjectCardForm(StyledModelForm):
    class Meta:
        model = FeaturedProjectCard
        fields = [
            'title', 'category_name', 'budget_range', 'location',
            'timeline', 'vendor_quote_preview', 'bids_count',
            'status_tag', 'image', 'order', 'is_active'
        ]


class PackageCardForm(StyledModelForm):
    class Meta:
        model = PackageCard
        fields = [
            'title', 'subtitle', 'price', 'price_unit', 'original_price',
            'feature_bullets', 'filter_tag', 'cta_label', 'cta_url',
            'is_popular', 'order', 'is_active'
        ]
        widgets = {
            'feature_bullets': forms.Textarea(attrs={'rows': 4, 'placeholder': 'One feature per line...'}),
        }


class TestimonialForm(StyledModelForm):
    class Meta:
        model = Testimonial
        fields = [
            'client_name', 'client_role_or_company', 'avatar',
            'rating', 'service_taken', 'review_text',
            'order', 'is_active'
        ]
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 3}),
        }


class TrustMetricForm(StyledModelForm):
    class Meta:
        model = TrustMetric
        fields = [
            'icon_class', 'stat_number', 'label', 'order', 'is_active'
        ]
