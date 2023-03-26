# Stable Diffusion API Server

# 图片生成接口文档

可以申请域名，后续会用域名替换掉下面的服务器公网域名

## Stable Diffusion API Server

### request

| API-URL             | http://server_ip:port/txt2img                   |
| ------------------- |-------------------------------------------------|
| method              | POST                                            |
| header content-type | application/x-www-form-urlencoded;charset=utf-8 |

body:

```json
{
            prompt:'Anime girl putting her hair up',		// str，AI提示词  
            seed:10086,					// integer，随机数即可	
            num_outputs:1,		// integer		预期想生成的图片数量	范围：[1,4]
            width:d.512,		// integer  目标图片宽度		范围：(0,1024]
            height: 512,		// integer	目标图片高度		范围：(0,1024]
            num_inference_steps:30,		// integer 生成（扩散）您的图像所花费的步骤数，越大，则输出越准确 ，范围：(0,150]
            guidance_scale:7,					// integer 调整图像与您的提示的相似程度。较高的值越准确   范围：(0,20]
 }
```

### response

```json
{
    "images": [			// 生成的图片信息
        {
            "image_url": "https://20230320-1313366673.cos.ap-nanjing.myqcloud.com/a61b5473ac46fa684b6a5f2369e8dfc0",			// url
            "mime_type": "image/png",			// 类型
            "seed": 3090352432285578			// 种子
        },
        {
            "image_url": "https://20230320-1313366673.cos.ap-nanjing.myqcloud.com/229aa32b8038d095eecd7f888a415063",
            "mime_type": "image/png",
            "seed": 2639160526635093
        },
        {
            "image_url": "https://20230320-1313366673.cos.ap-nanjing.myqcloud.com/8b59ccf18006905f14cc6f25e067a2c2",
            "mime_type": "image/png",
            "seed": 5130928274806351
        }
    ],
    "status": "success"			// 状态信息
}
```

范例：

<img src="/Users/bytedance/Library/Application Support/typora-user-images/image-20230324021708785.png" alt="image-20230324021708785" style="zoom:67%;" />

## 基于图片+文字生成图片

### request

| API-URL             | http://server_ip:port/img2img                   |
| ------------------- |-------------------------------------------------|
| method              | POST                                            |
| header content-type | application/x-www-form-urlencoded;charset=utf-8 |

body:

```json
{
            prompt:'Anime girl putting her hair up',		// str，AI提示词  
            seed:10086,					// integer，随机数即可	
            num_outputs:1,		// integer		预期想生成的图片数量	范围：[1,4]
            num_inference_steps:30,		// integer 生成（扩散）您的图像所花费的步骤数，越大，则输出越准确 ，范围：(0,150]
            guidance_scale:7,					// integer 调整图像与您的提示的相似程度。较高的值越准确   范围：(0,20]
            strength: 0.7,							// 保持默认值即可,范围(0,1)
            init_image: '图片base64字符串'
            
 }
```

### response

同上

```json
{
    "images": [			// 生成的图片信息
        {
            "image_url": "https://20230320-1313366673.cos.ap-nanjing.myqcloud.com/a61b5473ac46fa684b6a5f2369e8dfc0",			// url
            "mime_type": "image/png",			// 类型
            "seed": 3090352432285578			// 种子
        },
        {
            "image_url": "https://20230320-1313366673.cos.ap-nanjing.myqcloud.com/229aa32b8038d095eecd7f888a415063",
            "mime_type": "image/png",
            "seed": 2639160526635093
        },
        {
            "image_url": "https://20230320-1313366673.cos.ap-nanjing.myqcloud.com/8b59ccf18006905f14cc6f25e067a2c2",
            "mime_type": "image/png",
            "seed": 5130928274806351
        }
    ],
    "status": "success"			// 状态信息
}
```



范例

<img src="/Users/bytedance/Library/Application Support/typora-user-images/image-20230324022021466.png" alt="image-20230324022021466" style="zoom:67%;" />

