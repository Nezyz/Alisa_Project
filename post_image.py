from requests import post
def post_image(skill_id, token, filename):
    url = f'https://dialogs.yandex.net/api/v1/skills/{skill_id}/images'
    files = {'file': open(filename, 'rb')}
    headers = {'Authorization': f'OAuth {token}'}
    s = post(url, files=files, headers=headers)
    print(s.json())


token = "AQAAAAACFWAxAAT7owUAyPAPHExvhBizbv_MIJI"
skill = "df580121-04cd-4e5c-aaff-13fd7077f6a4"
image = "tambov.jpg"
post_image(skill,token,image)
image = "moskva.jpg"
post_image(skill,token,image)
image = "voronezh.jpg"
post_image(skill,token,image)
image = "LeoMessi.jpg"
post_image(skill,token,image)