from components.interaction import FOCUS_LABELS


def test_phase5_focus_labels_cover_core_workspace_contexts():
    for key in ["health", "activity", "engineering", "testing", "documentation", "risk", "contributor", "language", "file"]:
        assert key in FOCUS_LABELS


def test_phase5_focus_labels_are_human_readable():
    assert FOCUS_LABELS["contributor"] == "Contributor"
    assert FOCUS_LABELS["file"] == "File"
