from google.appengine.ext import ndb, db
from protorpc import messages


class StringTranslation(ndb.Model):
    english = ndb.StringProperty()
    spanish = ndb.StringProperty()
    portuguese = ndb.StringProperty()


class TextTranslation(ndb.Model):
    english = ndb.TextProperty()
    spanish = ndb.TextProperty()
    portuguese = ndb.TextProperty()


class ChoiceTranslation(ndb.Model):
    keyname = ndb.StringProperty()
    english = ndb.StringProperty()
    spanish = ndb.StringProperty()
    portuguese = ndb.StringProperty()


class BlobKeyTranslation(ndb.Model):
    spanish = ndb.BlobKeyProperty()
    english = ndb.BlobKeyProperty()
    portuguese = ndb.BlobKeyProperty()


class StringTranslationProperty(ndb.StructuredProperty):
    def __init__(self, **kwds):
        super(StringTranslationProperty, self).__init__(StringTranslation, **kwds)


class StringTranslationMessage(messages.Message):
    english = messages.StringField(1)
    spanish = messages.StringField(2)
    portuguese = messages.StringField(3)


class TextTranslationProperty(ndb.StructuredProperty):
    def __init__(self, **kwds):
        super(TextTranslationProperty, self).__init__(TextTranslation, **kwds)


class TextTranslationMessage(messages.Message):
    english = messages.StringField(1)
    spanish = messages.StringField(2)
    portuguese = messages.StringField(3)


class ChoiceTranslationProperty(ndb.StructuredProperty):
    #   Definition: objectProperty = ChoiceTranslationProperty(sp_choices=('hola',...), en_choices=('hello',...),pt_choices=('ola',...))
    #   Initialization: object = Object(title = ChoiceTranslation(keyname= 'hello'))
    def __init__(self, choices=None, **kwds):
        self.choices = choices
        super(ChoiceTranslationProperty, self).__init__(ChoiceTranslation, **kwds)

    def _validate(self, value):
        if not value.keyname:
            if not self.exist_in_dictionary(self.choices, value.keyname):
                raise TypeError('The value %s is not a valid choice option, possible options are %s ' % (repr(value.keyname), repr(self.choices.keys())))

    def exist_in_dictionary(self, choices, searched_value):
        for key in choices.keys():
            if key == searched_value:
                return True
        return False

    def _to_base_type(self, value):
        english = None
        spanish = None
        portuguese = None
        try:
            english = self.choices[value.keyname]['english']
        except Exception:
            pass
        try:
            spanish = self.choices[value.keyname]['spanish']
        except Exception:
            pass
        try:
            portuguese = self.choices[value.keyname]['portuguese']
        except Exception:
            pass
        tmodel = ChoiceTranslation(keyname=value.keyname, english=english, spanish=spanish, portuguese=portuguese)
        return tmodel

    def __unicode__(self):
        return '%s' % (self)


class ChoiceTranslationMessage(messages.Message):
    keyname = messages.StringField(1)
    english = messages.StringField(2)
    spanish = messages.StringField(3)
    portuguese = messages.StringField(4)


class BlobKeyTranslationProperty(ndb.StructuredProperty):
    def __init__(self, **kwds):
        super(BlobKeyTranslationProperty, self).__init__(BlobKeyTranslation, **kwds)


class BlobKeyTranslationMessage(messages.Message):
    #TODO: Make tests with this property type
    english = messages.StringField(1)
    spanish = messages.StringField(2)
    portuguese = messages.StringField(3)


SHORTENED_LANGUAGES = {
    'en': 'english',
    'es': 'spanish',
    'pt': 'portuguese'
}


# Returns the object for the language in parameter. If it doesn't exist, it returns the object with the default language
def get_object_with_translation(modelname, id, language):
    all_objects = ndb.get_multi([ndb.Key(modelname, id + '-en'), ndb.Key(modelname, id + '-es'), ndb.Key(modelname, id + '-pt')])
    lenghten_language = SHORTENED_LANGUAGES[language]

    default_object = None
    selected_object_by_language = None
    selected_object = None
    if all_objects:
        for single_object in all_objects:
            if single_object is not None:
                if single_object.is_default:
                    default_object = single_object
                if single_object.item_language.keyname == lenghten_language:
                    selected_object_by_language = single_object
                if default_object is None:
                    default_object = single_object

        if selected_object_by_language is not None:
            selected_object = selected_object_by_language
        elif default_object is not None:
            selected_object = default_object

    return selected_object
