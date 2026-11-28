Shader "CottageGardenDecor/Demo/Gradient Sky"
{
    // Demo sky of Demo_CottageGarden (the series floating-island look, Farm Nature / Farm Machinery): a procedural vertical
    // gradient by the view direction. The shot cameras look 35-40 deg down, so most of the visible sky lies BELOW the
    // horizon: pale near the horizon (frame top), a deeper clean blue further down (frame bottom). Demo-only, removable.
    Properties
    {
        _ZenithColor ("Zenith Color", Color) = (0.52, 0.72, 0.94, 1)
        _HorizonColor ("Horizon Color", Color) = (0.84, 0.91, 0.97, 1)
        _BelowColor ("Below Color", Color) = (0.56, 0.76, 0.95, 1)
        _BelowSharpness ("Below Gradient Power", Range(0.3, 3)) = 0.9
        _Exposure ("Exposure", Range(0, 4)) = 1
    }
    SubShader
    {
        Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" "RenderPipeline"="UniversalPipeline" }
        Cull Off
        ZWrite Off
        Pass
        {
            Name "Sky"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ZenithColor;
                half4 _HorizonColor;
                half4 _BelowColor;
                float _BelowSharpness;
                float _Exposure;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 direction : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.positionCS.z = output.positionCS.w * UNITY_RAW_FAR_CLIP_VALUE;
                output.direction = input.positionOS.xyz;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float y = normalize(input.direction).y;
                half3 color = y >= 0 ? lerp(_HorizonColor.rgb, _ZenithColor.rgb, saturate(y))
                                     : lerp(_HorizonColor.rgb, _BelowColor.rgb, pow(saturate(-y), _BelowSharpness));
                return half4(color * _Exposure, 1.0);
            }
            ENDHLSL
        }
    }
    Fallback Off
}
