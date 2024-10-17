import graphene
from apps.master_data.models import EmailTemplates, EmailTemplatesTranslation
from django.core.management import call_command


class Migrate(graphene.Mutation):
    class Arguments:
        pass

    status = graphene.Boolean()

    def mutate(root, info):
        call_command('migrate')
        return Migrate(status=True)


class DatabaseDelete(graphene.Mutation):
    class Arguments:
        pass

    status = graphene.Boolean()

    def mutate(root, info):
        call_command('flush', "--noinput")
        return DatabaseDelete(status=True)


class AdminSuperCreate(graphene.Mutation):
    class Arguments:
        pass

    status = graphene.Boolean()

    def mutate(root, info):
        call_command('loaddata', 'data/master_admin.yaml')
        return AdminSuperCreate(status=True)

class ReloadDataEmailTemplate(graphene.Mutation):
    class Arguments:
        pass

    status = graphene.Boolean()

    def mutate(root, info):
        EmailTemplates.objects.all().delete()
        EmailTemplatesTranslation.objects.all().delete()
        call_command('loaddata', 'data/email_templates.yaml')
        call_command('loaddata', 'data/email_templates_translation.yaml')
        return ReloadDataEmailTemplate(status=True)


class MasterdataCopyEn(graphene.Mutation):
    class Arguments:
        pass

    status = graphene.Boolean()

    def mutate(root, info):
        call_command('masterdata_copy_en')
        return MasterdataCopyEn(status=True)


class Mutation(graphene.ObjectType):
    migrate_run = Migrate.Field()
    database_delete = DatabaseDelete.Field()
    master_data_copy_en = MasterdataCopyEn.Field()
    reload_data_email_template = ReloadDataEmailTemplate.Field()
    create_master_admin = AdminSuperCreate.Field()
