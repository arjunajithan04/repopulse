from components.loading import render_scan_loader, scan_styles


class FakeContainer:
    def __init__(self):
        self.markup = None
        self.unsafe_allow_html = None

    def markdown(self, markup, unsafe_allow_html=False):
        self.markup = markup
        self.unsafe_allow_html = unsafe_allow_html


def test_owner_avatar_is_revealed_after_repository_metadata():
    container = FakeContainer()
    render_scan_loader(
        container,
        "octocat/Hello-World",
        16,
        "Loading repository metadata",
        "Repository validated.",
        avatar_url="https://avatars.githubusercontent.com/u/583231?v=4",
        owner_login="octocat",
    )
    assert container.unsafe_allow_html is True
    assert 'class="rp-pulse-orb identity-revealed "' in container.markup
    assert 'src="https://avatars.githubusercontent.com/u/583231?v=4"' in container.markup
    assert "octocat" in container.markup
    assert "octocat/Hello-World" in container.markup
    assert 'class="rp-avatar-progress-ring"' in container.markup
    assert "stroke-dasharray:100" in scan_styles()
    assert "stroke-dashoffset:var(--ring-offset,100)" in scan_styles()
    assert "clip-path:inset" not in scan_styles()


def test_missing_avatar_uses_owner_initial_without_broken_image():
    container = FakeContainer()
    render_scan_loader(
        container,
        "octocat/Hello-World",
        16,
        "Loading repository metadata",
        owner_login="octocat",
    )
    assert ">O</div>" in container.markup
    assert "<img" not in container.markup
    assert "REPOSITORY OWNER" in container.markup


def test_untrusted_avatar_url_is_not_rendered():
    container = FakeContainer()
    render_scan_loader(
        container,
        "octocat/Hello-World",
        16,
        "Loading repository metadata",
        avatar_url='javascript:alert("x")',
        owner_login='octo<script>',
    )
    assert "javascript:" not in container.markup
    assert "<script>" not in container.markup
    assert "&lt;script&gt;" in container.markup


def test_avatar_ring_tracks_scan_progress_instead_of_finishing_immediately():
    low = FakeContainer()
    mid = FakeContainer()
    near_done = FakeContainer()
    render_scan_loader(low, "octocat/Hello-World", 16, "Loading repository metadata", avatar_url="https://avatars.githubusercontent.com/u/583231?v=4", owner_login="octocat")
    render_scan_loader(mid, "octocat/Hello-World", 55, "Loading issues", avatar_url="https://avatars.githubusercontent.com/u/583231?v=4", owner_login="octocat")
    render_scan_loader(near_done, "octocat/Hello-World", 94, "Checking API capacity", avatar_url="https://avatars.githubusercontent.com/u/583231?v=4", owner_login="octocat")
    assert "--ring-offset:84;" in low.markup
    assert "--ring-offset:45;" in mid.markup
    assert "--ring-offset:6;" in near_done.markup


def test_avatar_ring_completes_when_scan_completes():
    container = FakeContainer()
    render_scan_loader(container, "octocat/Hello-World", 100, "Finalizing repository intelligence", completed=True, avatar_url="https://avatars.githubusercontent.com/u/583231?v=4", owner_login="octocat")
    assert "--ring-offset:0;" in container.markup
