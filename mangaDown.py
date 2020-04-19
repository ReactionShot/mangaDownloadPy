#! python3
# download manga from kissmanga

import requests, os, time, img2pdf
from selenium import webdriver
import zipfile


def downloadManga(mangaName, create_pdf, create_cbz):
    baseUrl = "https://kissmanga.com/Manga/"
    os.makedirs("manga", exist_ok=True)
    os.chdir("manga")
    base_filename = mangaName.replace("/", "-")
    os.makedirs(base_filename, exist_ok=True)
    # Download the page.
    print("Downloading page %s..." % baseUrl + mangaName, end="")
    browser = webdriver.Firefox()
    browser.get(baseUrl + mangaName)  # handle exceptions here
    time.sleep(15)  # kissmanaga takes time to load (browser check) - give it time
    print(" - Done")
    # Find the URL of the comic image.
    comicElem = browser.find_element_by_css_selector("#divImage")
    eles = comicElem.find_elements_by_css_selector("*")
    if comicElem == []:
        print("Could not find comic images.")
    else:
        j = 1
        file_number = 1
        for i in eles:
            if j == (len(eles) / 2) + 1:
                break
            comicUrl = i.find_element_by_xpath(
                "/html/body/div[1]/div[4]/div[11]/p[" + str(j) + "]/img"
            ).get_attribute("src")
            j += 1
            # Download the image.
            print("Downloading image %s..." % (comicUrl))
            res = requests.get(comicUrl)
            res.raise_for_status()
            imageFile = open(
                os.path.join(
                    base_filename,
                    os.path.basename(base_filename + "-" + str(file_number) + ".jpg"),
                ),
                "wb",
            )
            file_number += 1
            for chunk in res.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()

    # creating a pdf
    os.chdir(base_filename)
    dl_file_list = [i for i in os.listdir(".") if i.endswith(".jpg")]
    if create_pdf:
        with open(base_filename + ".pdf", "wb") as f:
            f.write(img2pdf.convert(dl_file_list))
    if create_cbz:
        with zipfile.ZipFile(base_filename + ".cbz", "w") as cbz_file:
            for manga_page in dl_file_list:
                cbz_file.write(manga_page)
    browser.quit()  # The program is done, close the web browser.
    print("Done")


if __name__ == "__main__":
    # eg - Hajime-no-Ippo/Ch-1239----In-His-Hand
    name = input("Enter manga name and chapter no. in kissmanga format: ")
    mk_pdf = not input("Create PDF? [Y/n] ").strip().lower().startswith("n")
    mk_cbz = not input("Create CBZ? [Y/n] ").strip().lower().startswith("n")
    if not mk_cbz and not mk_pdf:
        print("You must create some type of file, defaulting to PDF")
        mk_pdf = True
    downloadManga(name, mk_pdf, mk_cbz)
