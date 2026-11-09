from rest_framework.permissions import BasePermission, SAFE_METHODS


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
        return request.user.is_superuser


IsPortfolioOwnerOrReadOnly = IsPortfolioOwnerOrEditorOrReadOnly
