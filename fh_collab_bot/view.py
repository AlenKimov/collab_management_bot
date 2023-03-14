from fh_collab_bot.models import Project


def short_project_representation(project: Project) -> str:
    project_info_message_parts = [f'[+{project.likes}/-{project.dislikes}]']
    if project.tss is not None:
        project_info_message_parts.append(f'({project.tss:04d})')
    project_info_message_parts.append(
        f'<a href="https://twitter.com/{project.twitter_handle}">{project.twitter_handle}</a>')
    if project.manager_telegram_id is not None:
        project_info_message_parts.append(f'⇨ {project.manager_telegram_id}')
    project_info_message = ' '.join(project_info_message_parts)
    return project_info_message


def full_project_representation(project: Project):
    project_info_message_parts = [short_project_representation(project)]
    if project.discord_url is not None or project.discord_admin_nickname is not None:
        if project.discord_url is not None:
            project_info_message_parts.append(f'Discord: {project.discord_url}')
        if project.discord_admin_nickname is not None:
            project_info_message_parts.append(f' | {project.discord_admin_nickname}')
    project_info_message = '\n'.join(project_info_message_parts)
    return project_info_message


def short_projects_representation(projects: list[Project]) -> str:
    project_info_message_parts = []
    for project in projects:
        project_info_message_parts.append(short_project_representation(project))
    project_info_message = '\n'.join(project_info_message_parts)
    return project_info_message
