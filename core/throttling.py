from rest_framework.throttling import UserRateThrottle

class TierUserThrottle(UserRateThrottle):
    scope='tier_user'
    rate='10/day'
    def get_rate(self):
        return self.rate
    
    def allow_request(self,request,view):
        if request.user.is_authenticated:
            tier = request.user.tier
            self.rate = '1000/day' if tier == 'premium' else '10/day'
        else:
            self.rate = '10/day'
        return super().allow_request(request,view)

    def get_cache_key(self,request,view):
        if request.user.is_authenticated:
            tier=request.user.tier
            ident=request.user.pk
        else:
            tier='anon'
            ident=self.get_ident(request)

        return self.cache_format % {
            'scope':f"{self.scope}_{tier}",
            'ident':ident
            }