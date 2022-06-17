import asyncio
import os
import warnings

from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page

from lib import determine_answer

CHROMIUM_EXECUTABLE = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
USER_DATA_DIR = os.path.join(os.getcwd(), 'user-data')

if (not os.path.exists(USER_DATA_DIR)):
    os.mkdir(USER_DATA_DIR)


async def main():
    while(True):
        invite_link = input("Enter invite link (or 'q' to exit): ")
        if (invite_link.strip() == 'q'):
            break
        await play_game(invite_link.strip())


async def play_game(invite_link):
    browser = await launch({
        'executablePath': CHROMIUM_EXECUTABLE,
        'userDataDir': USER_DATA_DIR,
        'headless': False,
        'defaultViewport': {'width': 1000, 'height': 900}
    })

    page = await browser.newPage()
    await page.goto(invite_link)

    previous_question = None

    while (True):
        current_question = await get_question_text(page)

        if (current_question.lower() == 'get ready'):
            await page.waitFor(1000)
            continue

        if (current_question == "Leaderboard"):
            if (await is_next_round(page)):
                if (previous_question != None):
                    print("\nWaiting for next round...")
                previous_question = None
                await page.waitFor(1000)
                continue
            else:
                await display_leaderboard(page)
                break

        if (previous_question != None and current_question == previous_question):
            # wait for next question
            await page.waitFor(1000)
            continue

        choices = await get_answer_choices(page)
        answer = determine_answer(current_question, choices)
        await select_answer(page, answer)
        previous_question = current_question

    await browser.close()


async def get_question_text(page: Page) -> str:
    selector = 'h2.MuiTypography-root.MuiTypography-h2'
    await page.waitForSelector(selector)
    element = await page.querySelector(selector)
    return await get_text_content(element)


async def get_answer_choices(page: Page):
    selector = 'div.MuiGrid-root.MuiGrid-item button div:last-child'
    await page.waitForSelector(selector, {'visible': True})
    elements = await page.querySelectorAll(selector)
    choices = []
    for element in elements:
        textContent = await get_text_content(element)
        choices.append(textContent)
    return choices


async def select_answer(page: Page, answer: str):
    selector = f'div.MuiGrid-root.MuiGrid-item button[value="{answer}"]'
    await page.waitForSelector(selector, visible=True)
    while (True):
        try:
            await page.click(selector)
            break
        except:
            await page.waitFor(1000)


async def is_next_round(page: Page):
    selector = 'button.MuiButton-fullWidth span.MuiButton-label'
    elementHandle = await page.querySelector(selector)
    if (elementHandle == None):
        return False
    text = await get_text_content(elementHandle)
    return text.lower() == "start next round"


async def display_leaderboard(page: Page):
    list = await page.querySelectorAll('ul.MuiList-root li')
    print('\nLEADERBOARD')
    for item in list:
        pElements = await item.querySelectorAll('p')
        name = await get_text_content(pElements[0])
        score = await get_text_content(pElements[1])
        print(f'{name}: {score}')
    print()


async def get_text_content(element: ElementHandle):
    return str(await (await element.getProperty('textContent')).jsonValue())

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    asyncio.get_event_loop().run_until_complete(main())
