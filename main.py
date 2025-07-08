# main.py
"""
🧠 심리 기반 게임 추천 챗봇

필요한 패키지 설치:
pip install streamlit anthropic requests

실행 방법:
streamlit run main.py
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
from sidebar import render_standard_sidebar

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

def main():
    st.title("🧠 심리 기반 게임 추천 챗봇 (실시간 가격 포함)")

    # 세션 상태 초기화
    if "history" not in st.session_state:
        st.session_state["history"] = []

    # 사용자 입력 영역
    user_name = st.text_input("이름을 알려주세요")
    user_input = st.text_input("당신의 생각이나 감정을 말해보세요:")

    # 🎮 플레이어 수 선택
    player_count = st.selectbox("함께 플레이할 인원 수는 몇 명인가요?", options=list(range(1, 11)), index=0)

    # 💰 가격 정보 입력
    user_price = st.text_input("원하는 게임 가격대가 있나요? (예: 10000원, $15 등)", placeholder="예: 20000원")

    if user_input and user_price:
        # 감정 분석
        emotion = analyze_sentiment(user_input)

        # 확장된 게임 데이터베이스에서 추천 게임 가져오기
        game_db = get_game_database()
        
        # 감정과 플레이어 수에 맞는 게임들 가져오기
        suggested_games = game_db.get_games_by_emotion_and_players(emotion, player_count, max_games=15)
        
        # 예산에 맞는 게임들 필터링
        budget_suitable_games = game_db.get_games_by_price_range(user_price)
        
        # 두 조건을 모두 만족하는 게임들 우선 선택
        priority_games = [game for game in suggested_games if game in budget_suitable_games]
        
        # 부족하면 감정/플레이어 수 조건만 만족하는 게임들 추가
        if len(priority_games) < 10:
            priority_games.extend([game for game in suggested_games if game not in priority_games])
        
        # 그래도 부족하면 다양한 게임들 추가
        if len(priority_games) < 10:
            diverse_games = game_db.get_random_diverse_games(count=15)
            priority_games.extend([game for game in diverse_games if game not in priority_games])

        # Claude 응답 생성
        system_prompt = f"""
당신은 사용자의 감정과 요구 조건에 맞춰 정확한 게임을 추천해주는 지능형 챗봇입니다.

🎯 목적:
- 사용자의 감정 상태, 희망 인원 수, 예산에 맞는 온라인 게임을 추천해주세요.
- 추천하는 게임은 반드시 실제로 존재하는 정확한 이름이어야 합니다.

📌 조건:
- 게임은 반드시 온라인 또는 디지털 플랫폼에서 구매 가능한 게임이어야 합니다.
- {player_count}명이 함께 플레이할 수 있어야 하며
- 예산 범위: '{user_price}' 이하
- 감정 상태: '{emotion}' — 이 감정에 어울리는 게임을 추천해주세요.

💡 추천 가능한 게임들 (참고용):
{', '.join(priority_games[:20])}

📝 응답 형식:
각 게임마다 다음 정보를 포함해주세요:
1. **게임명** (정확한 이름으로)
2. **장르 및 간단한 설명**
3. **플레이어 수 지원 여부**
4. **감정에 맞는 이유**
5. **왜 이 게임이 {player_count}명에게 적합한지**

⚠️ 주의사항:
- 존재하지 않는 게임은 추천하지 마세요.
- 게임명은 정확하게 적어주세요 (가격 조회에 사용됩니다).
- **정확히 3개의 게임만** 추천해주세요.
- 가격이나 링크 정보는 제공하지 마세요 (시스템에서 자동으로 추가됩니다).
- 위에 제공된 추천 가능한 게임들 중에서 선택하는 것을 권장합니다.
- 각 게임이 왜 현재 감정 상태와 인원수에 적합한지 구체적으로 설명해주세요.
"""

        try:
            with st.spinner("🤖 Claude가 게임을 추천하는 중..."):
                # Claude API 호출
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                )

                assistant_reply = message.content[0].text

            # 추천된 게임에서 게임 이름 추출
            game_names = extract_game_names_from_response(assistant_reply)
            
            if game_names:
                st.write("💰 **실시간 가격 정보 조회 중...**")
                price_api = get_price_api()
                
                # 각 게임의 가격 정보 조회
                game_prices = {}
                for game_name in game_names:
                    with st.spinner(f"🔍 '{game_name}' 가격 조회 중..."):
                        price_info = price_api.get_game_price_info(game_name)
                        game_prices[game_name] = price_info
                
                # 가격 정보와 함께 결과 표시
                st.write("## 🎮 추천 게임 목록")
                st.write(assistant_reply)
                
                st.write("---")
                st.write("## 💰 실시간 가격 정보")
                
                within_budget_games = []
                over_budget_games = []
                
                for game_name, price_info in game_prices.items():
                    price_display = format_price_display(price_info, game_name)
                    within_budget = check_price_within_budget(price_info, user_price)
                    
                    if price_info:  # Steam에서 가격 정보를 찾은 경우
                        if within_budget:
                            within_budget_games.append((game_name, price_display))
                            st.success(f"{price_display}")
                        else:
                            over_budget_games.append((game_name, price_display))
                            st.warning(f"⚠️ {price_display} (예산 초과 가능)")
                    else:  # Steam에서 찾을 수 없는 경우
                        within_budget_games.append((game_name, price_display))  # 무료일 가능성으로 예산 내로 간주
                        st.info(f"{price_display}")
                
                # Steam에서 찾은 게임과 못 찾은 게임 구분 안내
                steam_found_games = [name for name, info in game_prices.items() if info is not None]
                not_found_games = [name for name, info in game_prices.items() if info is None]
                
                if steam_found_games and not_found_games:
                    st.write("---")
                    st.success(f"✅ Steam에서 확인된 게임: {', '.join(steam_found_games)}")
                    st.info(f"🔍 Steam 외 플랫폼 게임: {', '.join(not_found_games)}")
                
                if not_found_games:
                    st.info("💡 Steam에서 확인되지 않은 게임들은 다음 플랫폼에서 이용 가능할 수 있습니다:")
                    st.info("   • Epic Games Store (무료 게임 많음)")
                    st.info("   • 모바일 앱스토어 (무료/프리미엄)")
                    st.info("   • 브라우저 게임 (대부분 무료)")
                    st.info("   • PlayStation, Xbox, Nintendo Switch")

                if over_budget_games:
                    st.info("💡 예산을 초과하는 게임들은 할인 시기를 노려보세요!")

            # 감정 기반 장르 추천
            if emotion == "부정":
                genre_recommendation = "🎮 힐링이 필요하시군요. 캐주얼, 힐링 게임을 추천해요!"
            elif emotion == "긍정":
                genre_recommendation = "⚔️ 지금 기분이 좋으시군요! 경쟁 게임을 즐겨보는 건 어떠세요?"
            else:
                genre_recommendation = "🤔 중립적인 감정인걸로 판단됩니다. 그렇다면 다양한 장르를 시도해보세요!"

            # 대화 저장
            st.session_state["history"].append(("👤 사용자", f"{user_name}: {user_input}"))
            st.session_state["history"].append(("📌 조건", f"인원수: {player_count}명 / 희망 가격: {user_price}"))
            st.session_state["history"].append(("🤖 챗봇", assistant_reply))

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {str(e)}")

    # 대화 기록 출력
    if st.session_state["history"]:
        st.write("---")
        st.write("## 📝 대화 기록")
        for speaker, text in reversed(st.session_state["history"]):
            st.markdown(f"**{speaker}:** {text}")

    # 사이드바 렌더링
    game_db = get_game_database()
    render_standard_sidebar(game_db)

if __name__ == "__main__":
    main()