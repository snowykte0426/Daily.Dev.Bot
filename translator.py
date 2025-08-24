import logging
import random
import time

import requests
from googletrans import Translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KoreanTranslator:
    def __init__(self):
        self.translator = None
        self._initialize_translator()

    def _initialize_translator(self):
        try:
            self.translator = Translator()
        except Exception as e:
            logger.error(f"번역기 초기화 실패: {str(e)}")

    def _translate_with_requests(self, text):
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',  # 자동 언어 감지
                'tl': 'ko',
                'dt': 't',
                'q': text
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                translated_parts = []
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    for item in data[0]:
                        if isinstance(item, list) and len(item) >= 1 and item[0]:
                            translated_parts.append(item[0])

                if translated_parts:
                    translated_text = ''.join(translated_parts)

                    detected_lang = data[2] if len(data) > 2 else 'unknown'
                    confidence = data[6] if len(data) > 6 else 0.0

                    logger.debug(f"Google API 번역 성공: {detected_lang} -> ko (신뢰도: {confidence:.2f})")
                    return translated_text

        except Exception as e:
            logger.debug(f"Google API 번역 실패: {str(e)}")

        return None

    def translate_to_korean(self, text, max_retries=3):
        if not text or text.strip() == "":
            return ""

        if any('\uac00' <= char <= '\ud7a3' for char in text):
            logger.debug("이미 한국어로 된 텍스트입니다.")
            return text

        logger.debug("Google API 직접 호출로 번역 시도...")
        api_result = self._translate_with_requests(text)
        if api_result:
            logger.debug(f"Google API 번역 성공: {text[:30]}... -> {api_result[:30]}...")
            return api_result

        logger.debug("Google API 실패, googletrans 라이브러리 시도 중...")
        for attempt in range(max_retries):
            try:
                if not self.translator:
                    self._initialize_translator()

                result = self.translator.translate(text, src='auto', dest='ko')

                if hasattr(result, 'text') and result.text:
                    translated_text = result.text
                    logger.debug(f"googletrans 번역 완료: {text[:30]}... -> {translated_text[:30]}...")
                    return translated_text
                else:
                    logger.debug(f"번역 결과에 text 속성이 없거나 비어있음: {type(result)}")

            except Exception as e:
                logger.debug(f"googletrans 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")

                if attempt < max_retries - 1:
                    time.sleep(random.uniform(0.5, 1.5))
                    self._initialize_translator()

        logger.warning(f"모든 번역 방법 실패, 원본 반환: {text[:50]}...")
        return text

    def translate_post(self, post):
        try:
            translated_post = post.copy()

            if post.get("title"):
                logger.info("제목 번역 중...")
                translated_post["title"] = self.translate_to_korean(post["title"])
                time.sleep(1)

            if post.get("description"):
                logger.info("설명 번역 중...")
                translated_post["description"] = self.translate_to_korean(post["description"])
                time.sleep(1)

            if post.get("content"):
                logger.info("본문 번역 중...")
                translated_post["content"] = self.translate_to_korean(post["content"])
                time.sleep(1)

            return translated_post

        except Exception as e:
            logger.error(f"게시글 번역 실패: {str(e)}")
            return post

    def translate_posts(self, posts):
        translated_posts = []

        for i, post in enumerate(posts):
            logger.info(f"게시글 {i + 1}/{len(posts)} 번역 중...")
            translated_post = self.translate_post(post)
            translated_posts.append(translated_post)

        logger.info(f"총 {len(translated_posts)}개 게시글 번역 완료")
        return translated_posts