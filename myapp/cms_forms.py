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
                field.widget.attrs.update({'class': 'toggle-checkbox'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'dropzone-input', 'accept': 'image/*'})
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
            'site_title': forms.TextInput(attrs={'placeholder': 'e.g. Infinity Ventures'}),
            'tagline': forms.TextInput(attrs={'placeholder': 'e.g. Instant Home Services & Custom Project Bidding Marketplace'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'e.g. support@infinityventures.in'}),
            'support_phone': forms.TextInput(attrs={'placeholder': 'e.g. +91 1800-000-0000'}),
            'address': forms.TextInput(attrs={'placeholder': 'e.g. Main Road, Ranchi, Jharkhand, India'}),
            'facebook_url': forms.URLInput(attrs={'placeholder': 'https://facebook.com/yourpage'}),
            'instagram_url': forms.URLInput(attrs={'placeholder': 'https://instagram.com/yourhandle'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/company/yourprofile'}),
            'twitter_url': forms.URLInput(attrs={'placeholder': 'https://twitter.com/yourhandle'}),
            'youtube_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/@yourchannel'}),
            'copyright_text': forms.TextInput(attrs={'placeholder': 'e.g. © 2026 Infinity Ventures Private Limited. All rights reserved.'}),
            'logo': forms.FileInput(attrs={'class': 'dropzone-input', 'accept': 'image/*', 'id': 'id_logo'}),
            'favicon': forms.FileInput(attrs={'class': 'dropzone-input', 'accept': 'image/*', 'id': 'id_favicon'}),
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
            'badge_text': forms.TextInput(attrs={'placeholder': 'e.g. TWO ENGINES. ONE PLATFORM.'}),
            'headline': forms.TextInput(attrs={'placeholder': 'e.g. India\'s Smartest Marketplace for Instant Services & Competitive Project Bidding'}),
            'subtext': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Explainer paragraph under the headline...'}),
            'cta_primary_text': forms.TextInput(attrs={'placeholder': 'e.g. Book Instant Service'}),
            'cta_primary_url': forms.TextInput(attrs={'placeholder': 'e.g. #packages'}),
            'cta_secondary_text': forms.TextInput(attrs={'placeholder': 'e.g. Post a Project'}),
            'cta_secondary_url': forms.TextInput(attrs={'placeholder': 'e.g. #bidding'}),
            'stat1_number': forms.TextInput(attrs={'placeholder': 'e.g. 4.8/5 rated'}),
            'stat1_label': forms.TextInput(attrs={'placeholder': 'e.g. by 25,000+ verified customers'}),
            'stat2_number': forms.TextInput(attrs={'placeholder': 'e.g. 100% background-verified'}),
            'stat2_label': forms.TextInput(attrs={'placeholder': 'e.g. Aadhaar, police check & insured pros'}),
            'stat3_number': forms.TextInput(attrs={'placeholder': 'e.g. 3 quotations in < 45 mins'}),
            'stat3_label': forms.TextInput(attrs={'placeholder': 'e.g. average bidding response time'}),
            'hero_image': forms.FileInput(attrs={'class': 'dropzone-input', 'accept': 'image/*', 'id': 'id_hero_image'}),
        }


class QuickServiceCardForm(StyledModelForm):
    class Meta:
        model = QuickServiceCard
        fields = [
            'title', 'subtitle', 'image', 'price', 'discount_price',
            'duration', 'category_tag', 'badge_text', 'order', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. AC Service & Deep Clean'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'e.g. Jet pump wash, gas check & filter clean'}),
            'duration': forms.TextInput(attrs={'placeholder': 'e.g. 45 mins'}),
            'category_tag': forms.TextInput(attrs={'placeholder': 'e.g. AC & Cooling'}),
            'badge_text': forms.TextInput(attrs={'placeholder': 'e.g. ★ 4.8'}),
            'image': forms.FileInput(attrs={'class': 'dropzone-input', 'accept': 'image/*', 'id': 'id_image'}),
        }


class FeaturedProjectCardForm(StyledModelForm):
    class Meta:
        model = FeaturedProjectCard
        fields = [
            'title', 'category_name', 'budget_range', 'location',
            'timeline', 'vendor_quote_preview', 'bids_count',
            'status_tag', 'image', 'order', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. 3BHK Full Interior Painting & Waterproofing'}),
            'category_name': forms.TextInput(attrs={'placeholder': 'e.g. Painting & Waterproofing'}),
            'budget_range': forms.TextInput(attrs={'placeholder': 'e.g. ₹25,000 – ₹35,000'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Ranchi, Jharkhand'}),
            'timeline': forms.TextInput(attrs={'placeholder': 'e.g. 5 Days'}),
            'vendor_quote_preview': forms.TextInput(attrs={'placeholder': 'e.g. 3 quotations from verified contractors'}),
            'status_tag': forms.TextInput(attrs={'placeholder': 'e.g. Top Rated'}),
            'image': forms.FileInput(attrs={'class': 'dropzone-input', 'accept': 'image/*', 'id': 'id_image'}),
        }


class PackageCardForm(StyledModelForm):
    class Meta:
        model = PackageCard
        fields = [
            'title', 'subtitle', 'price', 'price_unit', 'original_price',
            'feature_bullets', 'filter_tag', 'cta_label', 'cta_url',
            'is_popular', 'order', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. AC Service & Deep Clean'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'e.g. Jet pump wash, gas check, filter & drain cleaning'}),
            'filter_tag': forms.TextInput(attrs={'placeholder': 'e.g. cooling, cleaning, plumbing, electrical'}),
            'feature_bullets': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter features separated by new lines...'}),
            'cta_label': forms.TextInput(attrs={'placeholder': 'e.g. Book Instant'}),
            'cta_url': forms.TextInput(attrs={'placeholder': 'e.g. #instant'}),
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
            'client_name': forms.TextInput(attrs={'placeholder': 'e.g. Ananya Singh'}),
            'client_role_or_company': forms.TextInput(attrs={'placeholder': 'e.g. Ranchi, Jharkhand · 3BHK Painting'}),
            'service_taken': forms.TextInput(attrs={'placeholder': 'e.g. 3BHK Painting'}),
            'review_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Customer review quote...'}),
            'avatar': forms.FileInput(attrs={'class': 'dropzone-input', 'accept': 'image/*', 'id': 'id_avatar'}),
        }


class TrustMetricForm(StyledModelForm):
    class Meta:
        model = TrustMetric
        fields = [
            'icon_class', 'stat_number', 'label', 'order', 'is_active'
        ]
        widgets = {
            'icon_class': forms.TextInput(attrs={'placeholder': 'e.g. fa-solid fa-shield-halved'}),
            'stat_number': forms.TextInput(attrs={'placeholder': 'e.g. 100% or 4.8★'}),
            'label': forms.TextInput(attrs={'placeholder': 'e.g. Aadhaar & Police Verified Pros'}),
        }
