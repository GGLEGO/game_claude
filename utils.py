# utils.py
import re

def analyze_sentiment(text):
    """향상된 감정 분석 함수"""
    if not text:
        return "중립"
    
    text_lower = text.lower()
    
    # 긍정적인 키워드 (대폭 확장됨)
    positive_words = [
        # 기본 긍정어
        '행복', '기쁘', '좋', '신나', '즐거', '만족', '최고', '완벽', '성공', '승리',
        # 감정 표현 - 어근 포함
        '웃', '기분좋', '상쾌', '흥미', '재미', '놀라', '멋지', '훌륭', '대단', '즐겁',
        # 상태 표현
        '편안', '평온', '자신감', '활기', '에너지', '충만', '희망', '긍정', '밝',
        # 평가어
        '좋아', '사랑', '마음에', '인상적', '감동', '뿌듯', '자랑스', '감사', '고마',
        # 구어체/인터넷 용어
        'ㅎㅎ', 'ㅋㅋ', '굿', '나이스', '쿨', '짱', '대박', '개좋', '존좋', '킹왕짱',
        # 동사 어근
        '웃겨', '기뻐', '즐기', '좋아해', '사랑해', '만족해', '행복해'
    ]
    
    # 부정적인 키워드 (대폭 확장됨)
    negative_words = [
        # 기본 부정어
        '슬프', '우울', '화나', '짜증', '스트레스', '피곤', '지루', '실패', '힘들', '괴로',
        # 감정 표현 - 어근 포함
        '속상', '답답', '무기력', '절망', '불안', '걱정', '두려', '외로', '쓸쓸', '화가',
        # 상태 표현
        '아프', '아픈', '병든', '지친', '힘든', '어려운', '복잡', '번거로', '귀찮',
        # 평가어
        '싫어', '미워', '짜증나', '실망', '후회', '부담', '끔찍', '최악', '나쁘',
        # 구어체/인터넷 용어
        'ㅠㅠ', 'ㅜㅜ', '하', '아', '망했', '개싫', '존나', '빡쳐', '열받', '빡침',
        # 동사 어근
        '화내', '슬퍼', '울어', '싫어해', '미워해', '괴로워', '힘들어', '우울해'
    ]
    
    # 감정 강도를 고려한 점수 계산
    positive_score = 0
    negative_score = 0
    
    # 단어별 점수 계산 (부분 매칭 포함)
    for word in positive_words:
        if word in text_lower:
            # 감탄사나 강조 표현은 가중치 부여
            if word in ['최고', '완벽', '대박', '짱', '굿', '킹왕짱']:
                positive_score += 3
            elif word in ['즐거', '행복', '기쁘', '좋', '사랑']:
                positive_score += 2
            else:
                positive_score += 1
    
    for word in negative_words:
        if word in text_lower:
            # 강한 부정어는 가중치 부여
            if word in ['최악', '끔찍', '절망', '괴로', '빡쳐']:
                negative_score += 3
            elif word in ['화나', '화가', '슬프', '우울', '스트레스']:
                negative_score += 2
            else:
                negative_score += 1
    
    # 특정 패턴 추가 검사
    # "화가 나다", "기분이 나쁘다" 등
    if re.search(r'화가?\s*나', text_lower):
        negative_score += 2
    if re.search(r'기분이?\s*나쁘', text_lower):
        negative_score += 2
    if re.search(r'기분이?\s*좋', text_lower):
        positive_score += 2
    
    # "즐거워", "재미있어" 등의 어미 변화 감지
    if re.search(r'즐거워|재미있어|행복해|기뻐|좋아해', text_lower):
        positive_score += 2
    if re.search(r'슬퍼|우울해|화나|짜증나|싫어', text_lower):
        negative_score += 2
    
    # 이모티콘 체크
    if re.search(r'[😊😄😃😀🙂😁😆😂🤣😍🥰😘☺️😌😎🤗]', text):
        positive_score += 2
    
    if re.search(r'[😢😭😞😔😟😕🙁☹️😣😖😫😩😤😠😡🤬😰😨😧]', text):
        negative_score += 2
    
    # 문장 패턴 분석
    if re.search(r'(정말|너무|엄청|완전|매우).*(좋|행복|기쁘|즐거)', text_lower):
        positive_score += 2
    
    if re.search(r'(정말|너무|엄청|완전|매우).*(싫|슬프|힘들|스트레스|화)', text_lower):
        negative_score += 2
    
    # 부정문 처리 ("좋지 않다", "행복하지 않다")
    if re.search(r'(좋|행복|기쁘).*(않|안)', text_lower):
        negative_score += 2
        positive_score = max(0, positive_score - 1)
    
    # 디버깅용 로그 (개발자 확인용)
    # print(f"Text: {text}")
    # print(f"Positive score: {positive_score}, Negative score: {negative_score}")
    
    # 결과 판정 (임계값 낮춤)
    if positive_score > negative_score:  # 긍정이 더 클 때
        return "긍정"
    elif negative_score > positive_score:  # 부정이 더 클 때
        return "부정"
    else:
        return "중립"