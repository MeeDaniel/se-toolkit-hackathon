import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User, Excursion

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session, engine):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "TourStats API"


@pytest.mark.asyncio
async def test_create_user(client):
    """Test user creation"""
    response = await client.post(
        "/api/users/",
        json={"telegram_alias": "testuser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telegram_alias"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_user_case_insensitive(client):
    """Test user creation is case-insensitive"""
    # Create user with uppercase
    response1 = await client.post(
        "/api/users/",
        json={"telegram_alias": "TestUser"}
    )
    assert response1.status_code == 200
    
    # Try to create same user with lowercase - should return existing
    response2 = await client.post(
        "/api/users/",
        json={"telegram_alias": "testuser"}
    )
    assert response2.status_code == 200
    assert response1.json()["id"] == response2.json()["id"]


@pytest.mark.asyncio
async def test_get_existing_user(client):
    """Test getting existing user"""
    # Create user
    create_response = await client.post(
        "/api/users/",
        json={"telegram_alias": "existinguser"}
    )
    user_id = create_response.json()["id"]
    
    # Get user
    get_response = await client.get("/api/users/existinguser")
    assert get_response.status_code == 200
    assert get_response.json()["telegram_alias"] == "existinguser"


@pytest.mark.asyncio
async def test_create_excursion(client):
    """Test excursion creation"""
    # Create user first
    user_response = await client.post(
        "/api/users/",
        json={"telegram_alias": "excursionuser"}
    )
    user_id = user_response.json()["id"]
    
    # Create excursion
    response = await client.post(
        "/api/excursions/",
        json={
            "user_id": user_id,
            "number_of_tourists": 15,
            "average_age": 25.0,
            "vivacity_before": 0.8,
            "vivacity_after": 0.6,
            "interest_in_it": 0.9,
            "interests_list": "robotics AI tech"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["number_of_tourists"] == 15
    assert data["user_id"] == user_id


@pytest.mark.asyncio
async def test_get_statistics(client):
    """Test statistics endpoint"""
    # Create user
    user_response = await client.post(
        "/api/users/",
        json={"telegram_alias": "statsuser"}
    )
    user_id = user_response.json()["id"]
    
    # Create multiple excursions
    for i in range(3):
        await client.post(
            "/api/excursions/",
            json={
                "user_id": user_id,
                "number_of_tourists": 10 + i * 5,
                "average_age": 20.0 + i * 5,
                "vivacity_before": 0.7,
                "vivacity_after": 0.8,
                "interest_in_it": 0.8,
                "interests_list": "tech education"
            }
        )
    
    # Get statistics
    response = await client.get(f"/api/statistics/?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_excursions"] == 3
    assert data["avg_tourists_per_excursion"] == 15.0


@pytest.mark.asyncio
async def test_get_user_specific_excursions(client):
    """Test that users only see their own excursions"""
    # Create two users
    user1_response = await client.post("/api/users/", json={"telegram_alias": "user1"})
    user1_id = user1_response.json()["id"]
    
    user2_response = await client.post("/api/users/", json={"telegram_alias": "user2"})
    user2_id = user2_response.json()["id"]
    
    # Create excursions for each user
    await client.post(
        "/api/excursions/",
        json={
            "user_id": user1_id,
            "number_of_tourists": 10,
            "average_age": 25.0,
            "vivacity_before": 0.8,
            "vivacity_after": 0.6,
            "interest_in_it": 0.9,
            "interests_list": "tech"
        }
    )
    
    await client.post(
        "/api/excursions/",
        json={
            "user_id": user2_id,
            "number_of_tourists": 20,
            "average_age": 30.0,
            "vivacity_before": 0.7,
            "vivacity_after": 0.5,
            "interest_in_it": 0.6,
            "interests_list": "education"
        }
    )
    
    # Each user should only see their own excursions
    user1_excursions = await client.get(f"/api/excursions/?user_id={user1_id}")
    user2_excursions = await client.get(f"/api/excursions/?user_id={user2_id}")
    
    assert user1_excursions.status_code == 200
    assert user2_excursions.status_code == 200
    assert len(user1_excursions.json()) == 1
    assert len(user2_excursions.json()) == 1
    assert user1_excursions.json()[0]["number_of_tourists"] == 10
    assert user2_excursions.json()[0]["number_of_tourists"] == 20
