fied_on(self, modified_on):
        if timezone.localtime(self.instance.modified_on) != modified_on:
            raise ConflictValidationException()
        return modified_on
