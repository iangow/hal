def load_one_segment():
    import json
    from mirror.models import BiographySegment

    text = r'''
{
      "quote": "Frederic V. Salerno, 59\n       \n      \n     \n    \n   \n   \n    \n     \n      \n       \n      \n     \n    \n    \n     \n      \u00a0\u00a0\n     \n    \n    \n     \n      \n       Chairman of Lynch Interactive Corporation, Rye, NY (telecommunications), since 2002. Mr. Salerno retired from Verizon\nCommunications, formerly Bell Atlantic Corporation (\u201cBell Atlantic\u201d) White Plains, NY in 2002 after over 37 years of service in a variety of positions including Vice Chairman and Chief Financial Officer from June 2000 until his retirement.\nPrior to that position, Mr. Salerno served as Senior Executive Vice President and Chief Financial Officer of Bell Atlantic from August 1997. Mr. Salerno has been a Director of CEI and a Trustee of Con Edison of New York since July 2002. Director or\nTrustee, Akamai Technologies, Inc., AVNET, Inc., Bear Sterns Companies, Inc., Dun\u00a0&\u00a0Bradstreet, Manhattan College and Viacom,\u00a0Inc.", 
      "uri": "http://hal.marder.io/highlight/1047862/000095013003003007", 
      "permissions": {
        "read": [
          "group:__consumer__"
        ]
      }, 
      "username": "LaurelMcMechan@gmail.com", 
      "updated": "2015-07-02T18:22:09.282270+00:00", 
      "user": "alice", 
      "created": "2015-07-02T18:22:09.282246+00:00", 
      "text": "Salerno, Frederic", 
      "consumer": "mockconsumer", 
      "ranges": [
        {
          "start": "/table[34]/tbody/tr[14]/td[2]/font", 
          "end": "/table[34]/tbody/tr[16]/td", 
          "startOffset": 15, 
          "endOffset": 0
        }
      ], 
      "id": "AU5QASWDVxF_lhEmap2Y"
    }
'''

    d = json.loads(text)
    BiographySegment.get_or_create(**d)
