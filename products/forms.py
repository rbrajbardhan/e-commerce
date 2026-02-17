from django import forms
from .models import Review, Product

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 4,
                'placeholder': 'Share your thoughts on this gear...'
            }),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'image', 'available']
        
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            if name == 'available':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif name == 'image':
                field.widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})
            else:
                field.widget.attrs.update({
                    'class': 'form-control bg-dark text-white border-secondary shadow-none',
                    'placeholder': field.label
                })
        
        # Specific overrides for textareas
        self.fields['description'].widget.attrs.update({'rows': '4'})