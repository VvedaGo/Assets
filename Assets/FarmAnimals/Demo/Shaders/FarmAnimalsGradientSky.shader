// Demo-only URP skybox: a vertical gradient (zenith - horizon - below the horizon). The demo cameras look down at
// floating islands, so the part below the horizon is the backdrop. Used by M_Demo_Sky in the Farm Animals demo scenes.
Shader "FarmAnimals/Demo/URP Gradient Sky"
{
    Properties
    {
        _ZenithColor ("Zenith", Color) = (0.30, 0.55, 0.90, 1)
        _HorizonColor ("Horizon", Color) = (0.86, 0.91, 0.95, 1)
        _GroundColor ("Below horizon", Color) = (0.66, 0.79, 0.92, 1)
        _HorizonSharpness ("Horizon sharpness", Range(0.5, 8)) = 2
        _Exposure ("Exposure", Range(0, 3)) = 1
    }

    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off
        ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ZenithColor;
                half4 _HorizonColor;
                half4 _GroundColor;
                half _HorizonSharpness;
                half _Exposure;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 direction : TEXCOORD0; };

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.direction = input.positionOS.xyz;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                float y = normalize(input.direction).y;
                half3 color = y >= 0.0
                    ? lerp(_HorizonColor.rgb, _ZenithColor.rgb, pow(saturate(y), 1.0 / _HorizonSharpness))
                    : lerp(_HorizonColor.rgb, _GroundColor.rgb, saturate(-y * _HorizonSharpness * 2.0));
                return half4(color * _Exposure, 1.0);
            }
            ENDHLSL
        }
    }
    Fallback Off
}
