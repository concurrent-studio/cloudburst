from PIL import Image
from binascii import a2b_base64, b2a_base64
from io import BytesIO

def preview_to_image(media_preview):
    # Base64 to bytes
    preview_binary = [i for i in a2b_base64(media_preview)]
    # Common header to bytes
    header = [
        i
        for i in list(
            a2b_base64(
                "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABsaGikdKUEmJkFCLy8vQkc/Pj4/R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0cBHSkpNCY0PygoP0c/NT9HR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//AABEIABQAKgMBIgACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/AA=="
            )
        )
    ]
    header[162], header[160] = preview_binary[1:3]
    # Encode data to bytes from ISO-8859-1 codec
    data = "".join([chr(i) for i in header + preview_binary[3:]]).encode(
        "iso-8859-1"
    )
    # Create PIL Image from data
    image = Image.open(BytesIO(data)).show()

def image_to_preview(filepath):
    im = Image.open(filepath)
    w, h = im.size
    im = im.resize((42 if w >= h else int(42*w/h), 42 if h >= w else int(42*h/w))).show()
    # fp = BytesIO()
    # # img.save(output, format='JPEG')
    # data = fp.getvalue()

    
    # with open(filepath, "rb") as f:
    #     data = f.read()
    #     # data = [chr(i) for i in header + preview_binary[3:]]
    # data_list = [ord(i) for i in list(data.decode("iso-8859-1"))]
    # header = data_list[:607]
    # width = header[162]
    # height = header[160]
    # preview_binary = bytes(data_list[607:])
    
    # media_preview = b2a_base64(preview_binary)
    return media_preview

media_preview = "ACodwM8UgGeKUIchRyTQ0ZUnPBHWkIkQHb3x9KQ8DCng1ctB+7Y4JIIPt+I/rQ9uC+wAqNwA9s+pql1uVdJa66kIYr3weB+VS+avq/50xoWBPftk4Gf1qQwKDjcDipu/Md12RX8xQQAOfpViOQSMd2cDliO3vjvVNW5PSp7dyyt7ZP8ASm9ET3srj8vGWVTn5xx6gf4+lWLaJ7slgwXqTn1qjMctj+8adHKbfDL/ABDv2oS7jduhPJbFM7mBwcYz3/wqHYKck5cDIHrwOT9af5rUkgbXY//Z"
preview_to_image(media_preview)
response = image_to_preview("./test.jpg")
if media_preview == response:
    print("FUCK WE DID IT!!")
else:
    print(response)
