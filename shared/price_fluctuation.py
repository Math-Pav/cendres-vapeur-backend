from decimal import Decimal

class PriceFluctuation:
    """
    Système de variation des prix dynamique
    
    Formule:
    - Demande = consultations + (achats × 3)
    - Offre = stock_actuel / stock_initial
    - Ratio = Offre / Demande
    
    Logique:
    - Ratio < 1 (pénurie) → Prix ↑
    - Ratio > 1 (surstock) → Prix ↓
    - Ratio ≈ 1 (équilibre) → Prix stable
    """
    
    MAX_PRICE_CHANGE = 50 
    
    @staticmethod
    def calculate_demand(view_count: int, purchase_count: int) -> float:
        """
        Calcule le niveau de demande
        Les achats pèsent 3x plus que les consultations
        """
        return view_count + (purchase_count * 3)
    
    @staticmethod
    def calculate_supply_ratio(current_stock: int, base_stock: int, demand: float) -> float:
        """
        Calcule le ratio offre/demande
        
        Offre = stock_actuel / stock_initial (en %)
        Ratio = Offre / Demande
        """
        if demand == 0:
            return 1.0
        
        if base_stock == 0:
            return 1.0
        
        supply_percentage = (current_stock / base_stock) * 100
        return supply_percentage / max(demand, 1)
    
    @staticmethod
    def calculate_price_change(supply_ratio: float) -> float:
        """
        Calcule la variation % du prix en fonction de l'offre/demande
        
        Si supply_ratio < 1:  Pénurie → Prix ↑
            - Plus bas le ratio, plus fort la hausse
            - Formule: (1 - ratio) × 100
        
        Si supply_ratio > 1: Surstock → Prix ↓
            - Plus haut le ratio, plus forte la baisse
            - Formule: -(ratio - 1) × 30
        
        Si supply_ratio ≈ 1: Équilibre → Prix stable
        """
        if supply_ratio < 1:
            price_change = (1 - supply_ratio) * 100
            price_change = min(price_change, PriceFluctuation.MAX_PRICE_CHANGE)
        else:
            price_change = -(supply_ratio - 1) * 30
            price_change = max(price_change, -PriceFluctuation.MAX_PRICE_CHANGE)
        
        return price_change
    
    @staticmethod
    def calculate_new_price(
        base_price: float,
        current_price: float,
        current_stock: int,
        base_stock: int,
        view_count: int,
        purchase_count: int
    ) -> dict:
        """
        Calcule le nouveau prix basé sur l'offre/demande
        
        Args:
            base_price: Prix de base initial
            current_price: Prix actuel
            current_stock: Stock restant
            base_stock: Stock initial
            view_count: Nombre de consultations
            purchase_count: Nombre d'achats
        
        Returns:
            Dict avec ancien prix, nouveau prix, % change, et indicateur
        """
        
        demand = PriceFluctuation.calculate_demand(view_count, purchase_count)
        
        supply_ratio = PriceFluctuation.calculate_supply_ratio(
            current_stock, base_stock, demand
        )
        
        price_change_percent = PriceFluctuation.calculate_price_change(supply_ratio)
        
        new_price = Decimal(str(current_price)) * (
            Decimal(1) + Decimal(str(price_change_percent)) / Decimal(100)
        )
        
        min_price = Decimal(str(base_price)) * Decimal('0.1')
        max_price = Decimal(str(base_price)) * Decimal('2.0')
        new_price = max(min_price, min(max_price, new_price))
        
        indicator = PriceFluctuation.get_trend_indicator(price_change_percent)
        
        return {
            'old_price': float(current_price),
            'new_price': float(new_price),
            'price_change_percent': price_change_percent,
            'indicator': indicator,
            'supply_ratio': supply_ratio,
            'demand': int(demand),
            'stock': current_stock
        }
    
    @staticmethod
    def get_trend_indicator(price_change_percent: float) -> dict:
        """
        Retourne l'indicateur visuel (flèche, couleur)
        """
        if price_change_percent > 5:
            return {
                'arrow': ' ↑',
                'trend': 'UP',
                'color': 'green',
                'label': f'+{price_change_percent:.2f}%'
            }
        elif price_change_percent < -5:
            return {
                'arrow': ' ↓',
                'trend': 'DOWN',
                'color': 'red',
                'label': f'{price_change_percent:.2f}%'
            }
        else:
            return {
                'arrow': ' →',
                'trend': 'STABLE',
                'color': 'gray',
                'label': f'{price_change_percent:.2f}%'
            }