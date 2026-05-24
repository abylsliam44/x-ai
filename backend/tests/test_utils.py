"""
Unit tests for utility functions: text processing and security helpers.
No database, no network, no LLM — pure deterministic logic.
"""
import pytest

# ─── text utils ──────────────────────────────────────────────────────────────

from app.utils.text import (
    bm25_like_score,
    chunk_text,
    extract_claim_candidates,
    normalize_whitespace,
    split_sentences,
    tokenize,
)


class TestTokenize:
    def test_basic(self):
        assert tokenize("Hello, World!") == ["hello", "world"]

    def test_empty(self):
        assert tokenize("") == []

    def test_numbers(self):
        assert "42" in tokenize("There are 42 items")

    def test_lowercase(self):
        tokens = tokenize("FastAPI SQLAlchemy")
        assert tokens == ["fastapi", "sqlalchemy"]

    def test_special_chars_stripped(self):
        assert tokenize("foo@bar.com") == ["foo", "bar", "com"]


class TestSplitSentences:
    def test_empty(self):
        assert split_sentences("") == []

    def test_single_sentence(self):
        assert split_sentences("Hello world") == ["Hello world"]

    def test_multiple_sentences(self):
        result = split_sentences("First. Second. Third.")
        assert result == ["First.", "Second.", "Third."]

    def test_exclamation_and_question(self):
        result = split_sentences("What? Yes! No.")
        assert len(result) == 3

    def test_whitespace_only(self):
        assert split_sentences("   ") == []

    def test_strips_whitespace_around_sentences(self):
        result = split_sentences("  Hello.   World.  ")
        assert all(s == s.strip() for s in result)


class TestChunkText:
    def test_empty(self):
        assert chunk_text("") == []

    def test_short_text_returns_one_chunk(self):
        text = "Short text."
        assert chunk_text(text, chunk_size=700) == [text]

    def test_long_text_produces_multiple_chunks(self):
        text = "x" * 1500
        chunks = chunk_text(text, chunk_size=700, overlap=100)
        assert len(chunks) > 1

    def test_all_chunks_nonempty(self):
        text = "a" * 2000
        chunks = chunk_text(text, chunk_size=700, overlap=100)
        assert all(len(c) > 0 for c in chunks)

    def test_first_chunk_correct_size(self):
        text = "y" * 1000
        chunks = chunk_text(text, chunk_size=700, overlap=0)
        assert len(chunks[0]) == 700

    def test_overlap_means_chunks_share_content(self):
        text = "a" * 800
        chunks = chunk_text(text, chunk_size=700, overlap=100)
        # The second chunk starts 600 chars into the first chunk
        assert len(chunks) == 2
        assert chunks[0][-100:] == chunks[1][:100]

    def test_exact_size(self):
        text = "b" * 700
        assert chunk_text(text, chunk_size=700) == [text]


class TestNormalizeWhitespace:
    def test_multiple_spaces(self):
        assert normalize_whitespace("a  b   c") == "a b c"

    def test_newlines(self):
        assert normalize_whitespace("a\nb\n\nc") == "a b c"

    def test_tabs(self):
        assert normalize_whitespace("a\t\tb") == "a b"

    def test_leading_trailing(self):
        assert normalize_whitespace("  hello  ") == "hello"

    def test_empty(self):
        assert normalize_whitespace("") == ""


class TestBm25LikeScore:
    def test_empty_doc(self):
        assert bm25_like_score(["ai"], []) == 0.0

    def test_no_match(self):
        score = bm25_like_score(["python"], ["java", "rust"])
        assert score == 0.0

    def test_exact_match_positive(self):
        score = bm25_like_score(["ai"], ["ai", "ai", "models"])
        assert score > 0

    def test_more_matches_higher_score(self):
        score_one = bm25_like_score(["ai"], ["ai"])
        score_many = bm25_like_score(["ai", "model"], ["ai", "model", "ai"])
        assert score_many > score_one

    def test_empty_query(self):
        assert bm25_like_score([], ["ai", "model"]) == 0.0


class TestExtractClaimCandidates:
    def test_empty_text(self):
        result = extract_claim_candidates("")
        assert result == []

    def test_sentence_with_number_selected(self):
        text = "There are 42 companies. Nothing else matters."
        candidates = extract_claim_candidates(text)
        assert any("42" in c for c in candidates)

    def test_keyword_triggers_selection(self):
        text = "Research shows this is effective. Nice weather today."
        candidates = extract_claim_candidates(text)
        assert any("Research shows" in c for c in candidates)

    def test_fallback_to_first_sentence(self):
        text = "A quiet observation. Another quiet one."
        candidates = extract_claim_candidates(text)
        # Neither sentence has a number or keyword; fallback = first sentence
        assert len(candidates) >= 1
        assert "A quiet observation" in candidates[0]

    def test_max_six_candidates(self):
        sentences = [f"There are {i} items." for i in range(10)]
        text = " ".join(sentences)
        candidates = extract_claim_candidates(text)
        assert len(candidates) <= 6

    def test_multiple_keywords(self):
        text = (
            "The majority of teams use this. Studies confirm the trend. "
            "All engineers agree. This is always the case."
        )
        candidates = extract_claim_candidates(text)
        assert len(candidates) >= 3


# ─── security utils ──────────────────────────────────────────────────────────

from app.core.security import (
    create_access_token,
    decode_token,
    decrypt_secret,
    encrypt_secret,
    generate_pkce_pair,
    generate_state_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        h = hash_password("mypassword")
        assert h != "mypassword"

    def test_correct_password_verifies(self):
        h = hash_password("secret123")
        assert verify_password("secret123", h) is True

    def test_wrong_password_fails(self):
        h = hash_password("secret123")
        assert verify_password("wrong", h) is False

    def test_hashes_are_unique(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        # bcrypt adds a random salt so hashes differ even for the same input
        assert h1 != h2


class TestTokenEncryption:
    def test_roundtrip(self):
        plaintext = "super_secret_token_xyz"
        assert decrypt_secret(encrypt_secret(plaintext)) == plaintext

    def test_encrypted_differs_from_plaintext(self):
        plaintext = "my_api_token"
        assert encrypt_secret(plaintext) != plaintext

    def test_two_encryptions_produce_different_ciphertext(self):
        # Fernet uses a random IV, so same plaintext → different ciphertext
        ct1 = encrypt_secret("hello")
        ct2 = encrypt_secret("hello")
        assert ct1 != ct2


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token("user-abc-123")
        payload = decode_token(token)
        assert payload["sub"] == "user-abc-123"

    def test_extra_claims_included(self):
        token = create_access_token("user-42", extra_claims={"role": "admin"})
        payload = decode_token(token)
        assert payload["role"] == "admin"

    def test_invalid_token_raises(self):
        with pytest.raises(ValueError):
            decode_token("not.a.valid.jwt")

    def test_tampered_token_raises(self):
        token = create_access_token("user-xyz")
        tampered = token[:-4] + "XXXX"
        with pytest.raises(ValueError):
            decode_token(tampered)

    def test_expiry_field_present(self):
        token = create_access_token("user-1")
        payload = decode_token(token)
        assert "exp" in payload


class TestPKCE:
    def test_verifier_min_43_chars(self):
        verifier, _ = generate_pkce_pair()
        assert len(verifier) >= 43

    def test_challenge_is_base64url(self):
        _, challenge = generate_pkce_pair()
        assert "+" not in challenge
        assert "/" not in challenge
        assert "=" not in challenge

    def test_verifier_and_challenge_differ(self):
        verifier, challenge = generate_pkce_pair()
        assert verifier != challenge

    def test_each_call_produces_unique_pair(self):
        pairs = {generate_pkce_pair()[0] for _ in range(20)}
        assert len(pairs) == 20


class TestStateToken:
    def test_uniqueness(self):
        tokens = {generate_state_token() for _ in range(50)}
        assert len(tokens) == 50

    def test_non_empty(self):
        assert len(generate_state_token()) > 0
