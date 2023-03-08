def short_project_data_representation(project_data: dict) -> str:
    project_info_message_parts = [f'[+{project_data["likes"]}/-{project_data["dislikes"]}]']
    if project_data['tss'] is not None:
        project_info_message_parts.append(f'({project_data["tss"]:04d})')
    project_info_message_parts.append(f'<a href="https://twitter.com/{project_data["twitter_handle"]}">{project_data["twitter_handle"]}</a>')
    if project_data['manager_telegram_id'] is not None:
        project_info_message_parts.append(f'⇨ {project_data["manager_telegram_id"]}')
    project_info_message = ' '.join(project_info_message_parts)
    return project_info_message


def full_project_data_representation(project_data: dict):
    project_info_message_parts = [short_project_data_representation(project_data)]
    if project_data['discord_url'] is not None or project_data['discord_admin_nickname'] is not None:
        if project_data['discord_url'] is not None:
            project_info_message_parts.append(f'Discord: {project_data["discord_url"]}')
        if project_data['discord_admin_nickname'] is not None:
            project_info_message_parts.append(f' | {project_data["discord_admin_nickname"]}')
    if project_data['note'] is not None:
        project_info_message_parts.append(f'\n{project_data["note"]}')
    project_info_message = '\n'.join(project_info_message_parts)
    return project_info_message


def short_project_data_list_representation(projects_data: list[dict]) -> str:
    project_info_message_parts = []
    for project_data in projects_data:
        project_info_message_parts.append(short_project_data_representation(project_data))
    project_info_message = '\n'.join(project_info_message_parts)
    return project_info_message
