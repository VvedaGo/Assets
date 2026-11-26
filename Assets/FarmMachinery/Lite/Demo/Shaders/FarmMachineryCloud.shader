Shader "FarmMachinery/Demo/Cloud"
{
    // Demo clouds (DEM-06): unlit gradient by the face normal - bright white tops, soft cool blue-grey sides and undersides,
    // a small facet accent from the main light direction. Not lit by the warm key or the brown trilight ground, so the
    // clouds stay white like the Farm Nature demo clouds.
    Properties
    {
        _TopColor ("Top Color", Color) = (1.0, 1.0, 1.0, 1)
        _SideColor ("Side Color", Color) = (0.90, 0.93, 0.98, 1)
        _BottomColor ("Bottom Color", Color) = (0.72, 0.80, 0.92, 1)
        _FacetAccent ("Facet Accent", Range(0, 0.3)) = 0.08
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Name "Cloud"
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _TopColor;
                half4 _SideColor;
                half4 _BottomColor;
                half _FacetAccent;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 normalWS : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 n = normalize(input.normalWS);
                half3 col = n.y >= 0 ? lerp(_SideColor.rgb, _TopColor.rgb, n.y) : lerp(_SideColor.rgb, _BottomColor.rgb, -n.y);
                col += _FacetAccent * (saturate(dot(n, GetMainLight().direction)) - 0.5);
                return half4(col, 1);
            }
            ENDHLSL
        }
        // depth for the SSAO / depth-normals passes of the shared renderer
        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On
            ColorMask R
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct Attributes { float4 positionOS : POSITION; };
            float4 Vert(Attributes input) : SV_POSITION { return TransformObjectToHClip(input.positionOS.xyz); }
            half Frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }
    Fallback Off
}
