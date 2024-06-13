class NaverRankDto():
    def __init__(self, storeName):
        self.storeName = storeName
        self.excludedAdRank = 0     # 실제 순위
        self.rank = 0               # 노출 순위
        self.isAdvertising = False      # 광고 여부
        self.isPriceComparision = False     # 가격 비교 여부
        self.comparisionRank = 0        # 가격 비교 순위
        self.productTitle = None      # 상품명
        self.price = 0      # 가격
        self.page = 0       # 노출 페이지
        self.mallProductId = None     # 상품 id
        
        self.reviewCount = 0    # 리뷰 개수
        self.scoreInfo = 0      # 리뷰 평점
        self.registrationDate = None        # 등록일
        self.thumbnailUrl = None      # 썸네일 이미지
        self.purchaseCount = 0      # 구매 건수
        self.keepCount = 0      # 찜 개수
        self.deliveryFee = 0        # 배송비
        self.category1Name = None       # 카테고리1
        self.category2Name = None       # 카테고리2
        self.category3Name = None       # 카테고리3
        self.category4Name = None       # 카테고리4
        self.lowMallCount = 0       # 가격비교 쇼핑몰 개수

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

    def setReviewCount(self, reviewCount):
        self.reviewCount = reviewCount

    def setScoreInfo(self, scoreInfo):
        self.scoreInfo = scoreInfo

    def setRegistrationDate(self, registrationDate):
        self.registrationDate = registrationDate

    def setThumbnailUrl(self, thumbnailUrl):
        self.thumbnailUrl = thumbnailUrl

    def setPurchaseCount(self, purchaseCount):
        self.purchaseCount = purchaseCount

    def setKeepCount(self, keepCount):
        self.keepCount = keepCount

    def setDeliveryFee(self, deliveryFee):
        self.deliveryFee = deliveryFee

    def setCategory1Name(self, category1Name):
        self.category1Name = category1Name

    def setCategory2Name(self, category2Name):
        self.category2Name = category2Name

    def setCategory3Name(self, category3Name):
        self.category3Name = category3Name

    def setCategory4Name(self, category4Name):
        self.category4Name = category4Name

    def setLowMallCount(self, lowMallCount):
        self.lowMallCount = lowMallCount