def save_extra_data(user, response, *args, **kwargs):
    user.bio = response.get("bio")
    user.location = response.get("location")
    user.save()
