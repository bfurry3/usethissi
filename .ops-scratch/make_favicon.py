from PIL import Image, ImageDraw
S=512
def icon(size):
    im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,S-1,S-1],radius=110,fill=(10,11,20,255))
    # vertical purple->pink gradient bolt
    mask=Image.new("L",(S,S),0); md=ImageDraw.Draw(mask)
    md.polygon([(300,40),(110,290),(240,290),(200,472),(402,212),(270,212),(330,40)],fill=255)
    g=Image.new("RGBA",(S,S))
    for y in range(S):
        t=y/S; c=(int(167+(124-167)*t),int(139+(58-139)*t),int(250+(237-250)*t),255)
        ImageDraw.Draw(g).line([(0,y),(S,y)],fill=c)
    im.paste(g,(0,0),mask)
    return im.resize((size,size),Image.LANCZOS)
icon(256).save("static/favicon.ico",sizes=[(16,16),(32,32),(48,48),(64,64)])
icon(192).save("static/icon-192.png"); icon(180).save("static/apple-touch-icon.png"); icon(256).save(".ops-scratch/favicon-preview.png")
