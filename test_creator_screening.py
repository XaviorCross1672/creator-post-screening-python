from creator_screening import CreatorPost, screen_post


def test_caption_with_sensitive_term_is_rejected_before_upload():
    post = CreatorPost("c-1", "A stolen design reveal", "reveal.png", b"image")
    result = screen_post(post)
    assert result.decision == "rejected"
    assert "stolen" in result.reason
    assert result.upload is None


def test_clean_caption_is_approved_without_network_client():
    post = CreatorPost("c-2", "New print from today's drop", "print.png", b"image")
    assert screen_post(post).decision == "approved"
