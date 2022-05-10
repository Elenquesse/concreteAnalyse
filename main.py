from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from rc_analyse import analyse_section
from transform_dict import SHAPE_TRANSFORM_DICT, STEEL_TRANSFORM_DICT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/concrete/")
async def analyse_cross_section(section_shape: str = "rectangle", section_height: int = 500, section_width: int = 250,
                                concrete_grade: int = 30,
                                steel_grade: str = "HPB300", steel_num: int = 4, steel_d: int = 20, steel_a: int = 35):
    # print(section_shape, section_height, section_width, concrete_grade, steel_grade, steel_num, steel_d, steel_a)
    section_shape = SHAPE_TRANSFORM_DICT[section_shape]
    steel_grade = STEEL_TRANSFORM_DICT[steel_grade]
    ka, mo = analyse_section(section_shape, [section_width, section_height],
                             steel_grade, [steel_num, steel_d, steel_a], concrete_grade)
    # ka, mo = analyse_section(0, [250, 500], 0, [4, 20, 35], 30)
    return {"kappa": ka, "moment": mo}
