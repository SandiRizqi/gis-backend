from celery import shared_task


@shared_task(bind=True)
def update_deforestations(self):
    for i in range(10):
        print(i)
    return "Done"