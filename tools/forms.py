from django import forms
from .models import AiTool  # Replace with your actual model name

class AIToolForm(forms.ModelForm):
    keywords = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput', 'placeholder': 'Enter tags separated by commas'})
    )

    class Meta:
        model = AiTool  # Replace with your actual model name
        
        fields = ['url', 'favicon', 'title', 'description', 'keywords', 'paid']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter URL'}),
            'favicon': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Favicon URL'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tool Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tool Description'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_keywords(self):
        keywords = self.cleaned_data.get('keywords')
        if isinstance(keywords, str):
            return [tag.strip() for tag in keywords.split(',')]  # Convert comma-separated string to list of tags
        return keywords
    
    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.user = user  # Assign the logged-in user
        if commit:
            instance.save()
        return instance
