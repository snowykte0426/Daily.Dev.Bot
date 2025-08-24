import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyDevScraper:
    def __init__(self):
        self.config = Config()
        self.driver = None

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver

    def dismiss_popups(self):
        try:
            close_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'OK')]",
                "//button[contains(text(), 'Close')]",
                "//button[@aria-label='Close']",
                "[data-testid='close-button']",
                ".close-button",
                "[role='dialog']",
                ".modal",
                ".overlay",
                ".popup"
            ]

            try:
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass

            for selector in close_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(1)
                        except:
                            continue
                except:
                    continue

            try:
                self.driver.execute_script("document.body.click();")
                time.sleep(1)
            except:
                pass

        except Exception as e:
            logger.debug(f"팝업 닫기 중 오류 (무시됨): {str(e)}")
            pass

    def wait_and_click(self, selector, timeout=10, by_type=By.CSS_SELECTOR):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by_type, selector))
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)

            self.dismiss_popups()

            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(2)

            return True

        except Exception as e:
            logger.warning(f"클릭 실패 ({selector}): {str(e)}")
            return False

    def click_show_more_buttons(self):
        try:
            show_more_selectors = [
                "//button[contains(text(), 'Show more')]",
                "//button[contains(text(), 'Read more')]",
                "//button[contains(text(), 'See more')]",
                "//a[contains(text(), 'Show more')]",
                "//a[contains(text(), 'Read more')]",
                "//span[contains(text(), 'Show more')]",
                "//span[contains(text(), 'Read more')]",

                "//button[contains(text(), '더보기')]",
                "//button[contains(text(), '더 보기')]",
                "//button[contains(text(), '전체보기')]",
                "//a[contains(text(), '더보기')]",

                "button[class*='show-more']",
                "button[class*='read-more']",
                "button[class*='expand']",
                ".show-more",
                ".read-more",
                ".expand-button",
                "[data-testid*='show-more']",
                "[data-testid*='read-more']",
                "[data-testid*='expand']",

                "button[aria-expanded='false']",
                "[role='button'][aria-expanded='false']"
            ]

            buttons_clicked = 0
            max_clicks = 3

            for selector in show_more_selectors:
                try:
                    if buttons_clicked >= max_clicks:
                        break

                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(1)

                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(2)

                                logger.debug(f"Show more 버튼 클릭됨: {selector}")
                                buttons_clicked += 1

                                if buttons_clicked >= max_clicks:
                                    break

                        except Exception as e:
                            logger.debug(f"버튼 클릭 실패: {str(e)}")
                            continue

                except Exception as e:
                    logger.debug(f"선택자 처리 실패: {selector} - {str(e)}")
                    continue

            if buttons_clicked > 0:
                logger.info(f"{buttons_clicked}개의 'Show more' 버튼을 클릭했습니다.")
                time.sleep(3)
            else:
                logger.debug("클릭 가능한 'Show more' 버튼을 찾지 못했습니다.")

        except Exception as e:
            logger.debug(f"Show more 버튼 클릭 중 오류: {str(e)}")

    def get_article_content(self, post_url, max_length=1000):
        try:
            if not post_url or not post_url.startswith('http'):
                return ""

            logger.info(f"본문 가져오기: {post_url[:50]}...")

            original_window = self.driver.current_window_handle
            self.driver.execute_script(f"window.open('{post_url}', '_blank');")

            new_window = None
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    new_window = window_handle
                    break

            if not new_window:
                logger.warning("새 탭을 열 수 없습니다")
                return ""

            self.driver.switch_to.window(new_window)

            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)

            self.click_show_more_buttons()

            content_selectors = [
                "article",
                "main article",
                ".post-content",
                ".article-content",
                ".content",
                ".entry-content",
                ".post-body",
                ".article-body",

                "[data-testid='article-content']",
                "[data-testid='post-content']",
                ".text-content",
                "main .prose",
                ".markdown-body",

                "div:has(> p)",
                "section:has(> p)"
            ]

            content_text = ""

            for selector in content_selectors:
                try:
                    content_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in content_elements:
                        text = element.text.strip()
                        if text and len(text) > 200:
                            content_text = text
                            break

                    if content_text:
                        break

                except Exception as e:
                    continue

            if not content_text:
                try:
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "p")
                    paragraph_texts = []

                    for p in paragraphs:
                        text = p.text.strip()
                        if text and len(text) > 30:
                            paragraph_texts.append(text)

                    if paragraph_texts:
                        content_text = "\n\n".join(paragraph_texts[:5])

                except Exception as e:
                    logger.warning(f"문단 수집 실패: {str(e)}")

            if content_text:
                if len(content_text) > max_length:
                    content_text = content_text[:max_length] + "..."

                logger.info(f"본문 수집 성공 ({len(content_text)}자)")
            else:
                logger.warning("본문 내용을 찾을 수 없습니다")

            self.driver.close()
            self.driver.switch_to.window(original_window)

            return content_text

        except Exception as e:
            logger.error(f"본문 가져오기 실패: {str(e)}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return ""

    def login_to_daily_dev(self):
        try:
            logger.info("daily.dev 로그인 시작")
            self.driver.get("https://app.daily.dev")

            time.sleep(5)
            self.dismiss_popups()

            login_selectors = [
                "//button[contains(text(), 'Log in')]",
                "button:contains('Log in')",
                "[data-testid='login-button']",
                ".login-button",
                "a[href*='login']"
            ]

            login_clicked = False
            for selector in login_selectors:
                by_type = By.XPATH if selector.startswith("//") else By.CSS_SELECTOR
                if self.wait_and_click(selector, timeout=5, by_type=by_type):
                    login_clicked = True
                    logger.info("로그인 버튼 클릭 성공")
                    break

            if not login_clicked:
                logger.error("로그인 버튼을 찾을 수 없습니다")
                return False

            time.sleep(3)
            email_login_selectors = [
                "//button[contains(text(), 'Continue with email')]",
                "button:contains('Continue with email')",
                "[data-testid='email-login']"
            ]

            email_clicked = False
            for selector in email_login_selectors:
                by_type = By.XPATH if selector.startswith("//") else By.CSS_SELECTOR
                if self.wait_and_click(selector, timeout=5, by_type=by_type):
                    email_clicked = True
                    logger.info("이메일 로그인 버튼 클릭 성공")
                    break

            if not email_clicked:
                logger.warning("이메일 로그인 버튼을 찾을 수 없습니다. 기본 로그인 폼을 찾아봅니다.")

            time.sleep(3)
            email_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']"
            ]

            email_field = None
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue

            if not email_field:
                logger.error("이메일 입력 필드를 찾을 수 없습니다")
                return False

            email_field.clear()
            email_field.send_keys(self.config.DAILY_DEV_EMAIL)
            logger.info("이메일 입력 완료")

            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']"
            ]

            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not password_field:
                logger.error("비밀번호 입력 필드를 찾을 수 없습니다")
                return False

            password_field.clear()
            password_field.send_keys(self.config.DAILY_DEV_PASSWORD)
            logger.info("비밀번호 입력 완료")

            submit_selectors = [
                "button[type='submit']",
                "//button[contains(text(), 'Sign in')]",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Continue')]",
                ".submit-button",
                "[data-testid='submit-button']"
            ]

            submit_clicked = False
            for selector in submit_selectors:
                by_type = By.XPATH if selector.startswith("//") else By.CSS_SELECTOR
                if self.wait_and_click(selector, timeout=5, by_type=by_type):
                    submit_clicked = True
                    logger.info("로그인 제출 버튼 클릭 성공")
                    break

            if not submit_clicked:
                logger.error("로그인 제출 버튼을 찾을 수 없습니다")
                return False

            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: "/feed" in driver.current_url or "/popular" in driver.current_url
                )
                logger.info("daily.dev 로그인 완료")
                return True

            except:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='feed'], article, .post"))
                    )
                    logger.info("daily.dev 로그인 완료 (피드 감지)")
                    return True
                except:
                    logger.error("로그인 후 피드를 찾을 수 없습니다")
                    return False

        except Exception as e:
            logger.error(f"로그인 실패: {str(e)}")
            return False

    def get_top_posts(self, limit=10):
        try:
            logger.info(f"상위 {limit}개 게시글 수집 시작")

            current_url = self.driver.current_url
            if "/feed" not in current_url and "/popular" not in current_url:
                self.driver.get("https://app.daily.dev/popular")
                time.sleep(5)

            self.dismiss_popups()

            logger.info("페이지 로딩 대기 중...")
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            except:
                pass

            time.sleep(5)
            post_selectors = [
                "article",
                "[data-testid='post']",
                "[data-testid='post-item']",
                ".post",
                ".post-item",
                "[data-testid='feed-item']",
                ".feed-item",
                ".card",
                "[role='article']",
                ".Card_card__BFnUM",
                "[class*='card']",
                "[class*='post']"
            ]

            post_elements = []
            for selector in post_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 2:
                        post_elements = elements
                        logger.info(f"게시글 요소 발견: {selector} ({len(elements)}개)")
                        break
                except:
                    continue

            if not post_elements:
                try:
                    logger.info("JavaScript로 게시글 요소 검색 중...")
                    js_elements = self.driver.execute_script("""
                        // 다양한 선택자로 요소 찾기
                        const selectors = ['article', '[data-testid*="post"]', '.card', '[class*="card"]', '[class*="post"]'];
                        for (let selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 2) {
                                console.log('Found elements with:', selector, elements.length);
                                return Array.from(elements).slice(0, 20); // 최대 20개
                            }
                        }
                        return [];
                    """)

                    if js_elements:
                        post_elements = js_elements
                        logger.info(f"JavaScript로 {len(post_elements)}개 게시글 요소 발견")
                except Exception as e:
                    logger.warning(f"JavaScript 검색 실패: {str(e)}")

            if not post_elements:
                with open("daily_dev_page_source_latest.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.error("게시글 요소를 찾을 수 없습니다. 페이지 소스가 저장되었습니다.")

                logger.info(f"현재 URL: {self.driver.current_url}")
                logger.info(f"페이지 제목: {self.driver.title}")

                return []

            logger.info("페이지 스크롤로 더 많은 게시글 로딩 중...")
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            posts = []
            logger.info(f"총 {len(post_elements)}개 요소에서 게시글 파싱 시작")

            for i, post_element in enumerate(post_elements[:limit * 2]):
                try:
                    title_selectors = [
                        "h1", "h2", "h3", "h4", "h5",
                        "[data-testid*='title']",
                        "[data-testid*='post-title']",
                        ".title",
                        ".post-title",
                        "a[href*='/posts/']",
                        "a[title]",
                        "[class*='title']"
                    ]

                    title = ""
                    title_element = None

                    for title_selector in title_selectors:
                        try:
                            title_element = post_element.find_element(By.CSS_SELECTOR, title_selector)
                            title = title_element.get_attribute("title") or title_element.text.strip()
                            if title and len(title) > 10:
                                break
                        except:
                            continue

                    if not title:
                        continue

                    link = ""
                    link_selectors = [
                        "a[href*='/posts/']",
                        "a[href*='http']",
                        "a[title]",
                        "a"
                    ]

                    for link_selector in link_selectors:
                        try:
                            link_element = post_element.find_element(By.CSS_SELECTOR, link_selector)
                            href = link_element.get_attribute("href")
                            if href and ("http" in href or "/posts/" in href):
                                link = href if href.startswith("http") else f"https://app.daily.dev{href}"
                                break
                        except:
                            continue

                    if not link and title_element:
                        try:
                            parent_link = title_element.find_element(By.XPATH, ".//ancestor::a[@href][1]")
                            href = parent_link.get_attribute("href")
                            if href:
                                link = href if href.startswith("http") else f"https://app.daily.dev{href}"
                        except:
                            pass

                    description = ""
                    desc_selectors = [
                        ".description",
                        ".summary",
                        "p",
                        ".content",
                        "[class*='description']",
                        "[class*='summary']"
                    ]

                    for desc_selector in desc_selectors:
                        try:
                            desc_element = post_element.find_element(By.CSS_SELECTOR, desc_selector)
                            desc_text = desc_element.text.strip()
                            if desc_text and len(desc_text) > 20:
                                description = desc_text[:300]
                                break
                        except:
                            continue

                    tags = []
                    try:
                        tag_elements = post_element.find_elements(By.CSS_SELECTOR,
                                                                  ".tag, [data-testid*='tag'], .badge, [class*='tag'], [class*='badge']")
                        tags = [tag.text.strip() for tag in tag_elements[:3]
                                if tag.text.strip() and len(tag.text.strip()) > 1]
                    except:
                        pass

                    if title and len(title) > 10:
                        content = ""
                        if self.config.FETCH_CONTENT and link and link.startswith('http'):
                            try:
                                content = self.get_article_content(link, max_length=800)
                            except Exception as e:
                                logger.warning(f"본문 가져오기 실패: {str(e)}")
                        elif not self.config.FETCH_CONTENT:
                            logger.info("본문 수집이 비활성화되어 있습니다.")

                        post_data = {
                            "title": title,
                            "link": link or f"https://app.daily.dev/search?q={title[:50]}",
                            "description": description,
                            "content": content,
                            "tags": tags
                        }

                        posts.append(post_data)
                        logger.info(f"게시글 {len(posts)}/{limit} 수집: {title[:50]}...")

                        if len(posts) >= limit:
                            break

                except Exception as e:
                    logger.warning(f"게시글 {i + 1} 처리 중 오류: {str(e)}")
                    continue

            logger.info(f"총 {len(posts)}개 게시글 수집 완료")
            return posts

        except Exception as e:
            logger.error(f"게시글 수집 실패: {str(e)}")
            return []

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def scrape_posts(self, limit=10):
        try:
            self.setup_driver()

            if self.config.DAILY_DEV_EMAIL and self.config.DAILY_DEV_PASSWORD:
                if not self.login_to_daily_dev():
                    logger.warning("로그인 실패. 로그인 없이 시도합니다.")
            else:
                logger.info("로그인 정보가 없습니다. 로그인 없이 시도합니다.")

            posts = self.get_top_posts(limit)
            return posts

        except Exception as e:
            logger.error(f"스크래핑 실패: {str(e)}")
            return []
        finally:
            self.close_driver()
