from rest_framework.permissions import BasePermission, SAFE_METHODS


def can_create_projects(user):
    return user.is_authenticated and user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    message = "This portfolio action is not allowed for your role."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method in ("PUT", "PATCH"):
            return request.user.is_superuser or request.user.groups.filter(
                name="Editor"
            ).exists()
        return can_create_projects(request.user)


IsPortfolioOwnerOrReadOnly = IsPortfolioOwnerOrEditorOrReadOnly
