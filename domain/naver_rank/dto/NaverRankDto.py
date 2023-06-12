class NaverRankDto():
    def __init__(self, storeName):
        self.storeName = storeName
        self.excludedAdRank = 0     # 실제 순위 
        self.rank = 0               # 노출 순위
        self.isAdvertising = False
        self.isPriceComparision = False
        self.comparisionRank = 0
        self.productTitle = ''
        self.price = 0
        self.page = 0
        self.mallProductId = ''

    def __repr__(self) -> str:
        return f"{type(self).__name__}(storeName={self.storeName}, excludedAdRank={self.excludedAdRank}, rank={self.rank}, isAdvertising={self.isAdvertising}, isPriceComparision={self.isPriceComparision}, comparisionRank={self.comparisionRank}, productTitle={self.productTitle}, price={self.price}))"

    def setStoreName(self, storeName):
        self.storeName = storeName

    def setExcludedAdRank(self, excludedAdRank):
        self.excludedAdRank = excludedAdRank

    def setRank(self, rank):
        self.rank = rank

    def setIsAdvertising(self, isAdvertising):
        self.isAdvertising = isAdvertising

    def setIsPriceComparision(self, isPriceComparision):
        self.isPriceComparision = isPriceComparision

    def setComparisionRank(self, comparisionRank):
        self.comparisionRank = comparisionRank

    def setProductTitle(self, productTitle):
        self.productTitle = productTitle
    
    def setPrice(self, price):
        self.price = price

    def setPage(self, page):
        self.page = page

    def setMallProductId(self, mallProductId):
        self.mallProductId = mallProductId