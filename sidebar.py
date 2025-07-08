# sidebar.py
import streamlit as st

def render_conversation_sidebar(current_step, user_data):
    """대화형 챗봇용 사이드바 렌더링"""
    
    with st.sidebar:
        st.write("## 💬 대화 진행 상황")
        
        steps = {
            "greeting": "👋 인사",
            "feeling": "😊 감정 파악",
            "players": "👥 플레이어 수",
            "budget": "💰 예산 설정",
            "recommendation": "🎮 게임 추천"
        }
        
        # 진행 상황 표시
        for step, label in steps.items():
            if step == current_step:
                st.write(f"▶️ **{label}** (현재)")
            elif (list(steps.keys()).index(step) < 
                list(steps.keys()).index(current_step)):
                st.write(f"✅ {label}")
            else:
                st.write(f"⏳ {label}")
        
        st.write("---")
        
        # 시스템 정보
        st.write("## ℹ️ 시스템 정보")
        st.write("- 🤖 Claude AI 추천")
        st.write("- 🔍 Steam 실시간 가격")
        st.write("- 🎮 200+ 게임 DB")
        st.write("- 💬 자연어 대화")
        
        # 대화 초기화 버튼
        if st.button("🗑️ 대화 초기화"):
            st.session_state.clear()
            st.rerun()
        
        st.write("---")
        
        # 현재 수집된 정보 표시
        if user_data:
            st.write("## 📝 수집된 정보")
            
            if "name" in user_data:
                st.write(f"👤 이름: {user_data['name']}")
            if "emotion" in user_data:
                st.write(f"😊 감정: {user_data['emotion']}")
            if "player_count" in user_data:
                st.write(f"👥 인원: {user_data['player_count']}명")
            if "budget" in user_data:
                st.write(f"💰 예산: {user_data['budget']}")

def render_standard_sidebar(game_database=None):
    """일반 형식용 사이드바 렌더링"""
    
    with st.sidebar:
        st.write("## ℹ️ 시스템 정보")
        st.write("- 🔍 Steam 실시간 가격 조회")
        st.write("- 🤖 Claude API 게임 추천")
        st.write("- 💰 예산 범위 자동 체크")
        st.write("- 🏷️ 할인 정보 표시")
        st.write("- 🎮 200+ 게임 데이터베이스")
        
        st.write("## 📊 지원 플랫폼")
        st.write("- Steam (주요)")
        st.write("- Epic Games (예정)")
        st.write("- 기타 플랫폼 (확장 예정)")
        
        st.write("## 🎯 지원 장르")
        st.write("- 🏆 경쟁/액션 게임")
        st.write("- 🌸 힐링/창조 게임") 
        st.write("- 🧩 퍼즐/전략 게임")
        st.write("- 👥 협동/파티 게임")
        st.write("- 📚 스토리/RPG 게임")
        st.write("- 🎨 인디/아트 게임")
        
        # 랜덤 게임 추천 기능 (게임 데이터베이스가 제공된 경우)
        if game_database:
            if st.button("🎲 랜덤 게임 보기"):
                random_games = game_database.get_random_diverse_games(count=5)
                st.write("**추천 게임들:**")
                for game in random_games:
                    st.write(f"• {game}")
        
        # 대화 기록 삭제 버튼
        if st.button("🗑️ 대화 기록 삭제"):
            st.session_state["history"] = []
            st.rerun()

def render_analytics_sidebar():
    """분석 정보용 사이드바 렌더링"""
    
    with st.sidebar:
        st.write("## 📊 추천 통계")
        
        # 세션 상태에서 통계 정보 가져오기
        if "recommendation_stats" in st.session_state:
            stats = st.session_state.recommendation_stats
            
            st.metric("총 추천 횟수", stats.get("total_recommendations", 0))
            st.metric("오늘 추천 횟수", stats.get("today_recommendations", 0))
            
            # 인기 장르
            if "popular_genres" in stats:
                st.write("### 🎮 인기 장르")
                for genre, count in stats["popular_genres"].items():
                    st.write(f"- {genre}: {count}회")
        
        st.write("---")
        
        st.write("## 🔧 설정")
        
        # 다크 모드 토글 (예시)
        dark_mode = st.checkbox("🌙 다크 모드", value=False)
        
        # 알림 설정
        notifications = st.checkbox("🔔 알림 켜기", value=True)
        
        # 언어 설정
        language = st.selectbox("🌐 언어", ["한국어", "English"], index=0)
        
        # 설정 저장
        if st.button("💾 설정 저장"):
            st.session_state.user_settings = {
                "dark_mode": dark_mode,
                "notifications": notifications,
                "language": language
            }
            st.success("설정이 저장되었습니다!")

def render_help_sidebar():
    """도움말용 사이드바 렌더링"""
    
    with st.sidebar:
        st.write("## ❓ 도움말")
        
        with st.expander("🎮 게임 추천 방법"):
            st.write("""
            1. 현재 감정 상태를 입력하세요
            2. 함께 플레이할 인원수를 선택하세요
            3. 예산 범위를 알려주세요
            4. AI가 맞춤 게임을 추천해드려요!
            """)
        
        with st.expander("💰 가격 정보"):
            st.write("""
            - Steam 실시간 가격 조회
            - 할인 정보 자동 확인
            - 예산 범위 내 게임 필터링
            - 다른 플랫폼 안내
            """)
        
        with st.expander("🔧 문제 해결"):
            st.write("""
            **게임을 찾을 수 없어요:**
            - 정확한 게임명을 입력해주세요
            - 다른 플랫폼에서 이용 가능할 수 있어요
            
            **추천이 마음에 안 들어요:**
            - 감정 상태를 더 구체적으로 입력해보세요
            - 다른 플레이어 수로 시도해보세요
            """)
        
        with st.expander("📞 문의하기"):
            st.write("""
            **버그 신고 또는 기능 제안:**
            - GitHub Issues
            - 이메일: support@gamebot.com
            - 디스코드: GameBot#1234
            """)
        
        st.write("---")
        
        # 버전 정보
        st.write("## 📋 정보")
        st.write("- 버전: v2.1.0")
        st.write("- 업데이트: 2024-07-04")
        st.write("- 개발자: GameBot Team")

def render_custom_sidebar(title, content_func, **kwargs):
    """커스텀 사이드바 렌더링"""
    
    with st.sidebar:
        if title:
            st.write(f"## {title}")
        
        # 사용자 정의 함수 실행
        if callable(content_func):
            content_func(**kwargs)

# 사이드바 유틸리티 함수들
def add_sidebar_metric(label, value, delta=None):
    """사이드바에 메트릭 추가"""
    with st.sidebar:
        st.metric(label, value, delta)

def add_sidebar_chart(data, chart_type="line"):
    """사이드바에 차트 추가"""
    with st.sidebar:
        if chart_type == "line":
            st.line_chart(data)
        elif chart_type == "bar":
            st.bar_chart(data)
        elif chart_type == "area":
            st.area_chart(data)

def add_sidebar_image(image_path, caption=None):
    """사이드바에 이미지 추가"""
    with st.sidebar:
        st.image(image_path, caption=caption)

def add_sidebar_download_button(data, filename, label="📥 다운로드"):
    """사이드바에 다운로드 버튼 추가"""
    with st.sidebar:
        st.download_button(
            label=label,
            data=data,
            file_name=filename,
            mime="text/plain"
        )