from django.db import models

class Vote(models.Model):
    # On utilise des guillemets ' ' pour éviter les erreurs d'import circulaire
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', related_name='votes', on_delete=models.CASCADE)
    
    # Ajout : Date du vote (utile pour les stats)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # RÈGLE D'OR : Un couple (user, product) doit être unique.
        # Impossible de voter deux fois pour le même objet.
        unique_together = ('user', 'product')

    def __str__(self):
        return f"Vote sur {self.product_id} par utilisateur {self.user_id}"