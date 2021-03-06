from django import forms

class SearchForm(forms.Form):
    INDEX_CHOICES = (
        (0, '0-indexed'),
        (1, '1-indexed'),
        )
    def __init__(self, assembly_choices, chrom_choices, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['assembly'] = forms.ChoiceField(initial=assembly_choices[0][0], label='Assembly to use',
                                     choices=assembly_choices)
        self.fields['chromosome'] = forms.ChoiceField(label='Chromosome', choices=chrom_choices)
        
        self.fields['indexing'] = forms.ChoiceField(initial=self.INDEX_CHOICES[0][0], label='Indexing to use',
                                     widget=forms.RadioSelect, choices=self.INDEX_CHOICES)
        self.fields['target_base'] = forms.IntegerField(label='Base to query')
        self.fields['number_around'] = forms.IntegerField(initial=0,label='Maximum number of bases around query to retrieve')
        
