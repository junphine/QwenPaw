# Design QA

## Scope

- 通用场景：产品经理、前端工程师、数据分析师和内容编辑协作上线数据看板。
- 桌面、移动端和深色主题均检查群标题、消息时间线、`@`、输入区和群资料。
- Agent 头像使用一致的 Ant Design Robot 图标，并按 Agent ID 稳定分配四种色调，不依赖领域硬编码或 emoji。

## Acceptance checks

1. 任意 Agent 名称和描述都能正常排版；重名时可显示唯一 `@ID`。
2. 普通消息、多成员 `@` 和 Agent 回复中的 `@` 都有清晰状态反馈。
3. 无可用 Agent 时新建页给出可执行空状态，发送按钮不可用。
4. 输入区在桌面和移动端保持可见；快捷提及在窄屏横向滚动。
5. 主动参与默认关闭，名称不再带领域含义。

## Evidence

- `qa/generic/01-room-desktop.png`：1440 × 1000，桌面浅色群聊。
- `qa/generic/02-room-mobile.png`：390 × 844，移动端浅色群聊。
- `qa/generic/03-room-dark.png`：610 × 806，深色群聊。
- `qa/generic/04-create-desktop.png`：1440 × 1000，通用 Agent 选择页。
- 浏览器实际发送 `@产品经理 @前端工程师 请一起给出上线方案`，两位成员按文本顺序分别回复。
- 群资料与成员管理展示四个任意角色及各自唯一 `@` 名称；弹窗按钮已本地化。
- 深色主题首轮发现引用文字对比度不足，补充深色引用样式后复查通过。
- 最终页面控制台 warning/error：0。

## Final result

passed
