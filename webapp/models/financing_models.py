from werkzeug.exceptions import BadRequest
from sqlalchemy import UniqueConstraint, desc
from sqlalchemy.dialects.sqlite import JSON
from webapp.extentions import db, cache
from webapp.functions.public import now as _now


class UserAsset(db.Model):
    """
    用户投资项目
    """
    id = db.Column(db.Integer(), primary_key=True)
    agent_id = db.Column(db.Integer(), db.ForeignKey('agent.id', ondelete='RESTRICT'), nullable=False)
    fp = db.Column(db.Integer(), db.ForeignKey('financial_product.id', ondelete='RESTRICT'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True))  # 第一次买入时间
    update_time = db.Column(db.DateTime(timezone=True), index=True)  # 最后更新时间
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=False)
    is_delete = db.Column(db.Boolean(), default=False)

    amounts = db.relationship(
        'UAAmount',
        backref='user_asset',
        lazy='dynamic'
    )
    details = db.relationship(
        'UADetail',
        backref='user_asset',
        lazy='dynamic'
    )

    __table_args__ = (
        UniqueConstraint('fp', 'agent_id', 'user_id', name='uix_ag_fp_user'),  # 联合唯一索引
    )

    def __init__(self, agent_id, fp, user_id):
        self.agent_id = agent_id
        self.fp = fp
        self.user_id = user_id
        db.session.add(self)
        db.session.flush()

    @property
    def fp_name(self):
        return FinancialProduct.name_cache().get(self.fp)

    @property
    def agent_name(self):
        return Agent.name_cache().get(self.agent_id)

    @property
    def last_amount(self):
        return self.amounts.order_by(desc('id')).first()

    @property
    def update_time_str(self):
        return self.update_time.strftime("%m-%d %H:%M")

    @staticmethod
    def clear_cache(model, operation):
        if operation == 'insert':
            # 新增持仓记录时，刷新用户的渠道缓存
            cache.delete('agent_user_{}'.format(model.user_id))


class UADetail(db.Model):
    """用户理财产品明细"""
    id = db.Column(db.Integer(), primary_key=True)
    userasset_id = db.Column(db.Integer(), db.ForeignKey('user_asset.id', ondelete='RESTRICT'), nullable=False)
    name = db.Column(db.String(32))
    expiration = db.Column(db.Date(), index=True)
    amount = db.Column(db.Integer(), default=0)
    update_time = db.Column(db.DateTime(timezone=True))
    meta = db.Column(JSON, default={})

    def __init__(self, userasset_id, name, expiration, amount, meta: dict = None):
        self.userasset_id = userasset_id
        self.name = name
        self.expiration = expiration
        self.amount = amount
        self.meta = meta or {}
        self.update_time = _now()
        db.session.add(self)
        db.session.commit()

    @property
    def amount_yuan(self):
        return round(self.amount / 100, 2)

    @classmethod
    def get(cls, detail_id, user_id):
        detail = cls.query.filter_by(id=detail_id).first()
        if not detail or detail.user_asset.user_id != user_id:
            raise BadRequest('理财产品错误')
        return detail


class UAAmount(db.Model):
    """
    用户理财产品金额变动历史
    """
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date())
    userasset_id = db.Column(db.Integer(), db.ForeignKey('user_asset.id', ondelete='RESTRICT'), nullable=False)
    amount = db.Column(db.Integer(), default=0)
    update_time = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint('userasset_id', 'date', name='uix_uaid_date'),  # 联合唯一索引
    )

    def __init__(self, ua_id, amount, now):
        self.userasset_id = ua_id
        self.amount = amount
        self.date = now.date()
        self.update_time = now
        db.session.add(self)
        db.session.flush()

    @property
    def amount_yuan(self):
        return round(self.amount / 100, 2)

    @staticmethod
    def update(ua_id, amount):
        now = _now()
        date = now.date()
        uaa = UAAmount.query.filter_by(date=date, userasset_id=ua_id).first()
        if uaa:
            uaa.amount = amount
            uaa.update_time = now
        else:
            uaa = UAAmount(ua_id, amount, now)
        return uaa

    @staticmethod
    def clear_cache(model, operation):
        cache.delete('user_asset_summary_{}'.format(model.user_asset.user_id))

    @property
    def update_time_str(self):
        return self.update_time.strftime("%m-%d %H:%M")


class Agent(db.Model):
    """购买处(银行/基金公司/支付宝/微信)"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), unique=True)
    assets = db.relationship(
        'UserAsset',
        backref='agent',
        lazy='dynamic'
    )

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def name_cache():
        cache_key = 'agent_name'
        if cache.get(cache_key):
            return cache.get(cache_key)
        name_dict = dict()
        for agent in Agent.query.order_by('id').all():
            name_dict[agent.id] = agent.name
        cache.set(cache_key, name_dict)
        return name_dict

    @staticmethod
    def clear_cache(model, operation):
        cache_keys = ['agent_name']
        cache.delete_many(*cache_keys)

    @staticmethod
    def user_agent(user_id):
        cache_key = 'agent_user_{}'.format(user_id)
        if cache.get(cache_key):
            return cache.get(cache_key)
        user_dict = dict()
        for agent in Agent.query.join(UserAsset).filter(
                Agent.id == UserAsset.agent_id,
                UserAsset.user_id == user_id,
        ).distinct().order_by(Agent.id).all():
            user_dict[agent.id] = agent.name
        cache.set(cache_key, user_dict)
        return user_dict


fp_assets = db.Table(
    'fp_assets',
    db.Column('fp_id', db.Integer(), db.ForeignKey('financial_product.id'), nullable=False),
    db.Column('fpa_id', db.Integer(), db.ForeignKey('fp_asset.id'), nullable=False),
    UniqueConstraint('fp_id', 'fpa_id', name='fp_fpa_unique')  # 联合唯一索引,name索引的名字
)


class FinancialProduct(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32), unique=True)
    code = db.Column(db.String(6), unique=True)  # 基金/股票 代码
    type_id = db.Column(db.Integer(), db.ForeignKey('fp_type.id', ondelete='RESTRICT'), nullable=False)
    url = db.Column(db.Text(), default='{}')
    meta = db.Column(db.Text(), default='{}')
    update_time = db.Column(db.DateTime(timezone=True))  # 更新时间
    assets = db.relationship(
        'FPAsset',
        secondary=fp_assets,
        backref=db.backref('fps', lazy='dynamic')
    )
    us_assets = db.relationship(
        'UserAsset',
        backref='financial_product',
        lazy='dynamic'
    )

    def __init__(self, name, type_id, code=None):
        self.name = name
        self.type_id = type_id
        self.code = code
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def name_cache():
        cache_key = 'fp_name'
        if cache.get(cache_key):
            return cache.get(cache_key)
        name_dict = dict()
        for fp in FinancialProduct.query.all():
            name_dict[fp.id] = fp.name
        cache.set(cache_key, name_dict)
        return name_dict

    @staticmethod
    def clear_cache(model, operation):
        cache_keys = ['fp_name']
        cache.delete_many(*cache_keys)


class FPAsset(db.Model):
    """
    金融产品的资产分布枚举： 股票、债券、现金、其他
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), unique=True)


class FPType(db.Model):
    """
    理财产品类型
    1银行存款 / 2货币基金 / 3债券基金 / 4股票基金 /  5股票 / 6银行理财 / 7保险理财 / 8贵金属 / 9混合基金 / 10现金
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(8), unique=True)
    fps = db.relationship(
        'FinancialProduct',
        backref='type',
        lazy='dynamic'
    )

    @staticmethod
    def dict():
        return {
            10: '现金',
            1: '银行存款',
            6: '银行理财',
            7: '保险理财',
            2: '货币基金',
            3: '债券基金',
            9: '混合基金',
            4: '股票基金',
            5: '股票',
            8: '贵金属',
        }
