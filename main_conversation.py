# main_conversational.py
"""
🧠 대화형 게임 추천 챗봇

필요한 패키지 설치:
pip install streamlit anthropic requests

실행 방법:
streamlit run main_conversational.py
"""

import streamlit as st
import anthropic
from game_price_api import GamePriceAPI
from game_utils import (
    extract_game_names_from_response,
    format_price_display,
    check_price_within_budget
)
from game_database import GameDatabase
from utils import analyze_sentiment
from sidebar import render_conversation_sidebar

# Anthropic 클라이언트 초기화
client = anthropic.Anthropic(
    api_key="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"  # 여기에 실제 Claude API 키를 입력하세요
)

# 게임 가격 API 인스턴스 생성
@st.cache_resource
def get_price_api():
    return GamePriceAPI()

# 확장된 게임 데이터베이스 인스턴스 생성
@st.cache_resource
def get_game_database():
    return GameDatabase()

def initialize_conversation():
    """대화 초기화"""
    if "conversation_step" not in st.session_state:
        st.session_state.conversation_step = "greeting"
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def add_message(role, message):
    """채팅 히스토리에 메시지 추가"""
    st.session_state.chat_history.append({"role": role, "message": message})

def display_chat_history():
    """채팅 히스토리 표시"""
    for chat in st.session_state.chat_history:
        if chat["role"] == "bot":
            with st.chat_message("assistant"):
                st.write(chat["message"])
        else:
            with st.chat_message("user"):
                st.write(chat["message"])

def get_step_prompt(step):
    """각 단계별 봇 메시지"""
    prompts = {
        "greeting": "안녕하세요! 🎮 저는 당신의 게임 추천 도우미입니다.\n\n먼저 이름을 알려주세요! 어떻게 불러드리면 될까요?",
        "feeling": "만나서 반가워요, {name}님! 😊\n\n오늘 기분이 어떠신가요? 현재 느끼고 있는 감정이나 생각을 자유롭게 말씀해주세요.\n예: \"오늘 정말 스트레스 받았어요\", \"기분이 너무 좋아요!\", \"그냥 평범한 하루예요\"",
        "players": "감정을 분석해보니 {emotion}적인 상태시군요! 🎯\n\n이번에는 함께 게임할 사람이 몇 명인지 알려주세요.\n혼자 플레이하실 건가요, 아니면 친구들과 함께 하실 건가요?",
        "budget": "총 {player_count}명이서 즐기실 예정이군요! 👥\n\n마지막으로 게임 예산이 어느 정도인지 알려주세요.\n예: \"2만원 정도\", \"무료 게임만\", \"돈은 상관없어요\"",
        "recommendation": "완벽해요! 모든 정보를 받았습니다. 🎉\n\n{name}님의 정보를 바탕으로 최적의 게임을 찾아드릴게요!\n\n📊 **분석 결과:**\n- 감정 상태: {emotion}\n- 플레이어 수: {player_count}명\n- 예산: {budget}\n\n잠시만 기다려주세요... 🔍"
    }
    return prompts.get(step, "")

def process_user_input(user_input, step):
    """사용자 입력 처리"""
    if step == "greeting":
        st.session_state.user_data["name"] = user_input
        st.session_state.conversation_step = "feeling"
        
    elif step == "feeling":
        st.session_state.user_data["feeling_text"] = user_input
        emotion = analyze_sentiment(user_input)
        st.session_state.user_data["emotion"] = emotion
        st.session_state.conversation_step = "players"
        
    elif step == "players":
        # 플레이어 수 추출
        import re
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            player_count = int(numbers[0])
        elif "혼자" in user_input or "1명" in user_input or "솔로" in user_input:
            player_count = 1
        elif "둘이" in user_input or "2명" in user_input or "커플" in user_input:
            player_count = 2
        elif "셋이" in user_input or "3명" in user_input:
            player_count = 3
        elif "넷이" in user_input or "4명" in user_input:
            player_count = 4
        else:
            player_count = 2  # 기본값
            
        st.session_state.user_data["player_count"] = player_count
        st.session_state.conversation_step = "budget"
        
    elif step == "budget":
        st.session_state.user_data["budget"] = user_input
        st.session_state.conversation_step = "recommendation"

def generate_game_recommendations():
    """게임 추천 생성"""
    user_data = st.session_state.user_data
    
    # 확장된 게임 데이터베이스에서 추천 게임 가져오기
    game_db = get_game_database()
    
    # 감정과 플레이어 수에 맞는 게임들 가져오기
    suggested_games = game_db.get_games_by_emotion_and_players(
        user_data["emotion"], 
        user_data["player_count"], 
        max_games=15
    )
    
    # 예산에 맞는 게임들 필터링
    budget_suitable_games = game_db.get_games_by_price_range(user_data["budget"])
    
    # 두 조건을 모두 만족하는 게임들 우선 선택
    priority_games = [game for game in suggested_games if game in budget_suitable_games]
    
    # 부족하면 감정/플레이어 수 조건만 만족하는 게임들 추가
    if len(priority_games) < 10:
        priority_games.extend([game for game in suggested_games if game not in priority_games])

    # Claude에게 개인화된 추천 요청
    system_prompt = f"""
당신은 친근하고 전문적인 게임 추천 전문가입니다.

사용자 정보:
- 이름: {user_data["name"]}
- 현재 감정: {user_data["emotion"]} (원문: "{user_data["feeling_text"]}")
- 플레이어 수: {user_data["player_count"]}명
- 예산: {user_data["budget"]}

추천 가능한 게임들: {', '.join(priority_games[:20])}

다음과 같이 응답해주세요:
1. {user_data["name"]}님께 친근하게 인사
2. 감정 상태를 공감하며 언급
3. 정확히 3개의 게임을 추천하되, 각 게임마다:
   - **게임명** (정확한 이름)
   - 간단한 설명과 장르
   - 왜 현재 감정과 인원수에 적합한지
   - 특별한 매력 포인트

따뜻하고 개인화된 톤으로 작성해주세요.
"""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {
                    "role": "user", 
                    "content": f"{user_data['name']}님을 위한 게임을 추천해주세요."
                }
            ]
        )
        
        recommendation_text = message.content[0].text
        
        # 게임 이름 추출 및 가격 조회
        game_names = extract_game_names_from_response(recommendation_text)
        
        if game_names:
            price_api = get_price_api()
            game_prices = {}
            
            # 가격 정보 조회
            for game_name in game_names:
                price_info = price_api.get_game_price_info(game_name)
                game_prices[game_name] = price_info
            
            return recommendation_text, game_prices
        
        return recommendation_text, {}
        
    except Exception as e:
        return f"죄송합니다, {user_data['name']}님. 추천을 생성하는 중 오류가 발생했습니다: {str(e)}", {}

def test_sentiment_analysis():
    """감정 분석 테스트"""
    st.write("## 🧠 감정 분석 테스트")
    
    test_cases = [
        "오늘 정말 행복해요! 😊",
        "너무 스트레스 받았어요 ㅠㅠ",
        "그냥 평범한 하루예요",
        "완전 최고! 대박이에요 ㅋㅋ",
        "짜증나고 화나요 😠",
        "기분이 좋지 않아요",
        "재미있고 즐거워요!",
        "우울하고 힘들어요...",
        "별로 특별할 게 없네요",
        "정말 끔찍하고 최악이에요",
        # 추가 테스트 케이스
        "화가 나요",
        "즐거워요",
        "매우 기뻐요",
        "조금 슬퍼요",
        "너무 좋아해요",
        "화가 났어요",
        "정말 재미있어요"
    ]
    
    st.write("### 테스트 케이스들:")
    for i, text in enumerate(test_cases, 1):
        emotion = analyze_sentiment(text)
        
        # 감정에 따른 색상 표시
        if emotion == "긍정":
            st.success(f"{i}. **{text}** → {emotion}")
        elif emotion == "부정":
            st.error(f"{i}. **{text}** → {emotion}")
        else:
            st.info(f"{i}. **{text}** → {emotion}")
    
    # 사용자 직접 테스트
    st.write("### 직접 테스트해보기:")
    user_text = st.text_input("감정을 표현해보세요:", key="sentiment_test")
    
    if user_text:
        emotion = analyze_sentiment(user_text)
        
        # 디버깅 정보 표시
        with st.expander("🔍 분석 과정 보기"):
            st.write(f"**입력 텍스트:** {user_text}")
            st.write(f"**소문자 변환:** {user_text.lower()}")
            
            # 감정 분석 내부 로직 시뮬레이션
            positive_keywords = ['행복', '기쁘', '좋', '즐거', '만족', '최고', '완벽', '즐겁', '사랑', '좋아']
            negative_keywords = ['슬프', '우울', '화나', '화가', '짜증', '스트레스', '힘들', '싫어', '최악']
            
            found_positive = [word for word in positive_keywords if word in user_text.lower()]
            found_negative = [word for word in negative_keywords if word in user_text.lower()]
            
            st.write(f"**찾은 긍정어:** {found_positive}")
            st.write(f"**찾은 부정어:** {found_negative}")
        
        if emotion == "긍정":
            st.balloons()
            st.success(f"분석 결과: **{emotion}** 😊")
        elif emotion == "부정":
            st.error(f"분석 결과: **{emotion}** 😔")
        else:
            st.info(f"분석 결과: **{emotion}** 😐")

def test_price_api():
    """가격 조회 API 테스트"""
    st.write("## 💰 가격 조회 테스트")
    
    # 테스트할 게임들 (Journey Steam 포함)
    test_games = [
        # 무료 게임들
        "Counter-Strike 2",
        "Valorant", 
        "League of Legends",
        "Apex Legends",
        "Fall Guys",
        # 유료 게임들
        "Stardew Valley",
        "Portal 2",
        "Overcooked! 2",
        "Terraria",
        "Hades",
        # Steam에 있는 Journey (2019년 출시)
        "Journey"
    ]
    
    price_api = get_price_api()
    
    st.write("### 게임 가격 조회 (무료/유료 포함):")
    
    for game in test_games:
        with st.expander(f"🎮 {game}"):
            with st.spinner(f"{game} 검색 중..."):
                # 가격 정보 조회
                price_info = price_api.get_game_price_info(game)
                
                if price_info:
                    # 무료 게임 확인
                    if price_info.get('price', 0) == 0:
                        st.success("🆓 무료 게임입니다!")
                    else:
                        st.success("💰 유료 게임입니다!")
                    
                    # 가격 정보 표시
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("가격", price_info['formatted'])
                    with col2:
                        if price_info.get('discounted', False):
                            st.metric("할인율", f"{price_info['discount_percent']}%")
                        else:
                            st.metric("할인율", "없음")
                    
                    if price_info.get('store_url'):
                        st.markdown(f"[Steam에서 보기]({price_info['store_url']})")
                        
                    # 상세 정보 (접을 수 있는 형태)
                    with st.expander("상세 정보"):
                        st.json(price_info)
                else:
                    st.error("❌ Steam에서 게임을 찾을 수 없음")
                    st.info("💡 다른 플랫폼(Epic Games, 모바일 등)에서 이용 가능할 수 있습니다.")
    
    # 무료 게임 추천 섹션
    st.write("---")
    st.write("### 🆓 추천 무료 게임들")
    
    game_db = get_game_database()
    free_games = game_db.games_by_price.get("무료", [])
    
    # 무료 게임을 3개씩 나누어 표시
    for i in range(0, min(12, len(free_games)), 3):
        cols = st.columns(3)
        for j, game in enumerate(free_games[i:i+3]):
            with cols[j]:
                st.write(f"🎮 **{game}**")
                if st.button(f"가격 확인", key=f"free_{i}_{j}"):
                    with st.spinner(f"{game} 확인 중..."):
                        price_info = price_api.get_game_price_info(game)
                        if price_info and price_info.get('price', 0) == 0:
                            st.success("✅ 무료 확인!")
                        elif price_info:
                            st.warning(f"💰 {price_info['formatted']}")
                        else:
                            st.info("❓ 확인 불가")
    

def show_debug_mode():
    """디버그 모드 표시"""
    st.write("## 🛠️ 시스템 상태")
    
    # 세션 상태 정보
    with st.expander("📊 세션 상태"):
        st.write("**현재 단계:**", st.session_state.get('conversation_step', 'None'))
        st.write("**수집된 데이터:**")
        st.json(st.session_state.get('user_data', {}))
        st.write("**채팅 기록 수:**", len(st.session_state.get('chat_history', [])))
    
    # 게임 데이터베이스 정보
    with st.expander("🎮 게임 데이터베이스"):
        game_db = get_game_database()
        
        # 감정별 게임 수 통계
        st.write("**감정별 게임 수:**")
        for emotion, genres in game_db.games_by_emotion.items():
            total_games = sum(len(games) for games in genres.values())
            st.write(f"- {emotion}: {total_games}개")
        
        # 플레이어 수별 게임 수
        st.write("**플레이어 수별 게임 수:**")
        for player_count, games in game_db.games_by_players.items():
            st.write(f"- {player_count}명: {len(games)}개")
    
    # API 연결 테스트
    with st.expander("🔗 API 연결 테스트"):
        if st.button("Steam API 테스트"):
            with st.spinner("Steam API 연결 테스트 중..."):
                price_api = get_price_api()
                test_result = price_api.get_game_price_info("Portal 2")
                
                if test_result:
                    st.success("✅ Steam API 연결 성공")
                    st.json(test_result)
                else:
                    st.error("❌ Steam API 연결 실패")
        
        # 감정 분석 테스트
        if st.button("감정 분석 테스트"):
            test_texts = ["행복해요", "슬퍼요", "보통이에요"]
            for text in test_texts:
                emotion = analyze_sentiment(text)
                st.write(f"'{text}' → {emotion}")

def main():
    st.title("🎮 대화형 게임 추천 챗봇")
    st.caption("자연스러운 대화를 통해 당신에게 완벽한 게임을 찾아드려요!")
    
    # 상단 탭으로 모드 선택
    tab1, tab2, tab3, tab4 = st.tabs(["💬 대화", "🧠 감정 테스트", "💰 가격 테스트", "🛠️ 디버그"])
    
    with tab1:
        # 기존 대화형 챗봇 로직
        initialize_conversation()
        
        # 채팅 히스토리 표시
        display_chat_history()
        
        current_step = st.session_state.conversation_step
        
        # 현재 단계에 따른 봇 메시지 표시
        if current_step == "recommendation":
            # 추천 생성 단계
            if len(st.session_state.chat_history) == 0 or st.session_state.chat_history[-1]["role"] != "recommendation":
                user_data = st.session_state.user_data
                
                # 추천 시작 메시지
                bot_message = get_step_prompt(current_step).format(**user_data)
                add_message("bot", bot_message)
                
                # 추천 생성
                with st.spinner("🤖 최적의 게임을 찾는 중..."):
                    recommendation_text, game_prices = generate_game_recommendations()
                
                # 추천 결과 표시
                with st.chat_message("assistant"):
                    st.write("## 🎯 맞춤 게임 추천")
                    st.write(recommendation_text)
                    
                    if game_prices:
                        st.write("### 💰 가격 정보 및 구매 링크")
                        for game_name, price_info in game_prices.items():
                            price_display = format_price_display(price_info, game_name)
                            if price_info:
                                st.success(price_display)
                            else:
                                st.info(price_display)
                
                # 추천 완료 표시
                add_message("recommendation", recommendation_text)
                
                # 다시 시작 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 새로운 추천 받기"):
                        st.session_state.conversation_step = "feeling"
                        st.session_state.user_data = {"name": st.session_state.user_data.get("name", "")}
                        st.rerun()
                
                with col2:
                    if st.button("🏠 처음부터 다시"):
                        st.session_state.clear()
                        st.rerun()
        
        else:
            # 일반 대화 단계
            if current_step in ["greeting", "feeling", "players", "budget"]:
                # 봇 메시지가 아직 표시되지 않았다면 표시
                if (len(st.session_state.chat_history) == 0 or 
                    st.session_state.chat_history[-1]["role"] != "bot"):
                    
                    user_data = st.session_state.user_data
                    bot_message = get_step_prompt(current_step).format(**user_data)
                    
                    with st.chat_message("assistant"):
                        st.write(bot_message)
                    add_message("bot", bot_message)
            
            # 사용자 입력 받기
            user_input = st.chat_input("메시지를 입력하세요...")
            
            if user_input:
                # 사용자 메시지 표시
                with st.chat_message("user"):
                    st.write(user_input)
                add_message("user", user_input)
                
                # 입력 처리
                process_user_input(user_input, current_step)
                st.rerun()
    
    with tab2:
        test_sentiment_analysis()
    
    with tab3:
        test_price_api()
    
    with tab4:
        show_debug_mode()
    
    # 사이드바 렌더링
    render_conversation_sidebar(
        st.session_state.get('conversation_step', 'greeting'), 
        st.session_state.get('user_data', {})
    )

if __name__ == "__main__":
    main()
