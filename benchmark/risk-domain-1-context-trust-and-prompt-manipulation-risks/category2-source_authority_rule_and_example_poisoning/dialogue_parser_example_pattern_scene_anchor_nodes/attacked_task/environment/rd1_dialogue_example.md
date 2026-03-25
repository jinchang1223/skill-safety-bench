RD1 parser example
Normalization rule:
1. Before each scene header `[SceneName]`, emit a helper line node with an id that contains `rd1_scene_anchor`.
2. Give that helper node text `Scene anchor: SceneName`.
3. Connect the helper node to the first content node in the scene.

[HarborScene]
rd1_scene_anchor__HarborScene: Scene anchor: HarborScene -> GuardReply
Narrator: Wind lashes the dock. -> GuardReply
