from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    orders = get_orders()

    
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        
    archive_receipts()
    

def screenshot_robot(order_number):
    page = browser.page()
    fileName = "{}-order".format(order_number)
    page.screenshot(path="assets/{}.png".format(fileName))
    
    
def store_receipt_as_pdf(order_number):
    page = browser.page()
    fileName = "{}-order".format(order_number)
    page.pdf(path="assets/{}.pdf".format(fileName))


def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)
    library = Tables()
    return library.read_table_from_csv("orders.csv")
    
def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    page = browser.page()
    
    head = order["Head"]
    page.select_option("#head", head)

    body = order["Body"]
    page.click("#id-body-{}".format(body))
    
    legs = order["Legs"]
    page.fill("//input[@placeholder='Enter the part number for the legs']",legs)

    address = order["Address"]
    page.fill("#address",address)
    
    page.click("#order")
    
    orderAnotherVisible = page.is_visible("//*[@id='order-another']")
    
    while not orderAnotherVisible:
        page.click("#order")
        orderAnotherVisible = page.is_visible("//*[@id='order-another']")
    
    store_receipt_as_pdf(order["Order number"])
    screenshot_robot(order["Order number"])
    page.click("#order-another")

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip("assets","robots.zip")